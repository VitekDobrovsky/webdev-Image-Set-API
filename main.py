from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import zipfile
import os
import io

app = FastAPI()

sizes = {
        "small": 420,
        "medium": 960,
        "extra_large": 1920
}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Set Generator API"}

@app.post("/generate-image-set/")
async def generate_image_set(max_width: int, file: UploadFile = File(...), name:str = "", transparent: bool = False):
    """
    Generate a set of images with different sizes from the uploaded image. 
    LEAVE THE NAME EMPTY IF YOU WANT TO KEEP THE SAME NAME AS THE UPLOADED FILE.
    """
    try:
        # Open the uploaded image
        img = Image.open(file.file)
        name = name if name != "" else os.path.splitext(file.filename)[0]

        if os.path.splitext(file.filename)[1] == ".png" and not transparent:
            raise HTTPException(status_code=400, detail="PNG images are not supported for this operation.")

        formats = ["png" if transparent else "jpeg", "webp"]
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
                    img_byte_arr = io.BytesIO()
                    img_resized.save(img_byte_arr, format=format.upper() if format != "jpeg" else "JPEG")
                    img_byte_arr.seek(0)
                    image_set.append((output_filename, img_byte_arr))
        
        # Compress the images into a zip file in memory
        zip_byte_arr = io.BytesIO()
        with zipfile.ZipFile(zip_byte_arr, "w") as zip:
            for filename, img_byte_arr in image_set:
                zip.writestr(filename, img_byte_arr.read())
        zip_byte_arr.seek(0)

        return StreamingResponse(zip_byte_arr, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=image_set.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

@app.get("/get-sizes/")
async def get_sizes():
    """
    Get the available sizes for the image set.
    """
    return sizes