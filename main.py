from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import zipfile
import os
from io import BytesIO

app = FastAPI()

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

sizes = {
        "small": 420,
        "medium": 960,
        "extra_large": 1920
}

def compress_images(zip_filename: str, image_files: list):
    with zipfile.ZipFile(zip_filename, "w") as zip:
        for image_file in image_files:
            zip.write(image_file, os.path.basename(image_file))

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Set Generator API"}

@app.post("/generate-image-set/")
async def generate_image_set(file: UploadFile = File(...), name:str = "Same as ipnut filename", transparent: bool = False, max_width: int = 1920):
    """
    Generate a set of images with different sizes from the uploaded image.
    """
    try:
        # Open the uploaded image
        img = Image.open(file.file)
        name = name if name != "Same as ipnut filename" else os.path.splitext(file.filename)[0]

        if os.path.splitext(file.filename)[1] == ".png" and not transparent:
            raise HTTPException(status_code=400, detail="PNG images are not supported for this operation.")

        formats = ["png" if transparent else "jpg", "webp"]
        _sizes = [size for size in sizes.values() if size < max_width]
        _sizes.append(max_width)

        # Generate and save images for each size
        image_set = []
        for size in _sizes:
            for format in formats:
                if max_width >= size:
                    img_resized = img.resize((size, int(size * img.height / img.width)))
                    
                    # Convert RGBA to RGB if saving as JPEG
                    if format in ["jpg", "jpeg"] and img_resized.mode == 'RGBA':
                        img_resized = img_resized.convert('RGB')
                    
                    output_filename = f"{name}-{size}x{size}.{format}"
                    output_path = os.path.join(output_dir, output_filename)
                    img_resized.save(output_path)
                    image_set.append(output_filename)
        
        # Compress the images into a zip file
        zip_filename = os.path.join(output_dir, "image_set.zip")
        compress_images(zip_filename, [os.path.join(output_dir, image) for image in image_set])


        return FileResponse(zip_filename, media_type="application/zip", filename="image_set.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

@app.get("/get-sizes/")
async def get_sizes():
    """
    Get the available sizes for the image set.
    """
    return sizes