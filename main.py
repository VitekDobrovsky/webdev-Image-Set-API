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

html = "<picture>"
html_sources = {
}

names = []

minimmum_step_size = 300

def generateHTML(available_formats: list, html_sources: dict):
    html = "<picture>"

    # Generate srcset attributes for each format in reverse order
    for format, sources in reversed(html_sources.items()):
        srcset = ", ".join(sources)
        html += f'<source srcset="{srcset}" type="image/{format}">'

    # Find the largest image across all formats for the img src attribute
    largest_image = max(
        html_sources[available_formats[0]],
        key=lambda x: int(x.split('-')[1].split('.')[0])
    ).split(' ')[0]

    # Generate sizes attribute based on the available sizes in html_sources
    sizes = ", ".join(
        f"(max-width: {int(img.split('-')[1].split('.')[0])}px) {int(img.split('-')[1].split('.')[0])}px"
        for img in sorted(
            {img for imgs in html_sources.values() for img in imgs},
            key=lambda x: int(x.split('-')[1].split('.')[0])
        )
    )

    html += f'<img src="{largest_image}" alt="Autoservis" sizes="{sizes}">'
    html += "</picture>"

    return html

def generateSimpleHTML(names: list, size: int, height: int):
    html = "<picture>"

    # Generate a single source element for each format
    for name in names:
        format = name.split('.')[0]
        html += f'<source srcset="{name}" type="image/{format}">'
    
    html += f'<img src="{names[0]}" alt="Autoservis" width={size} height={height}>'


    html += "</picture>"
    return html

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Set Generator API"}

@app.post("/generate-image-set-responsive/")
async def generate_image_set(max_width: int, file: UploadFile = File(...), name:str = "", transparent: bool = False):
    """
    Generate a set of images with different sizes from the uploaded image. 
    LEAVE THE NAME EMPTY IF YOU WANT TO KEEP THE SAME NAME AS THE UPLOADED FILE.
    """
    try:
        # Open the uploaded image
        img = Image.open(file.file)
        name = name if name != "" else os.path.splitext(file.filename)[0]

        formats = ["png" if transparent else "jpeg", "webp"]
        for format in formats:
            html_sources[format] = []
        _sizes = [size for size in sizes.values() if size < (max_width - minimmum_step_size)]
        _sizes.append(max_width)

        # Generate and save images for each size
        image_set = []
        for size in _sizes:
            for format in formats:
                img_resized = img.resize((size, int(size * img.height / img.width)))
                    
                # Convert RGBA to RGB if saving as JPEG
                if format in ["jpg", "jpeg"] and img_resized.mode == 'RGBA':
                    img_resized = img_resized.convert('RGB')
                    
                output_filename = f"{name}-{size}.{format}"
                img_byte_arr = io.BytesIO()
                img_resized.save(img_byte_arr, format=format.upper() if format != "jpeg" else "JPEG")
                img_byte_arr.seek(0)
                image_set.append((output_filename, img_byte_arr, size)) 

                html_sources[format].append(f"{output_filename} {size}w")
        

        html = generateSimpleHTML(formats, html_sources)

        # Compress the images into a zip file in memory
        zip_byte_arr = io.BytesIO()
        with zipfile.ZipFile(zip_byte_arr, "w") as zip:
            for filename, img_byte_arr, size in image_set:
                zip.writestr(filename, img_byte_arr.read())
            zip.writestr("index.html", html)
        zip_byte_arr.seek(0)

        return StreamingResponse(zip_byte_arr, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=image_set.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

@app.post("/generate-image-set/")
async def generate_image_set(desired_width: int, file: UploadFile = File(...), name: str = "", transparent: bool = False):
    """
    Generate two images in different formats at the desired size from the uploaded image.
    LEAVE THE NAME EMPTY IF YOU WANT TO KEEP THE SAME NAME AS THE UPLOADED FILE.
    """
    try:
        # Open the uploaded image
        img = Image.open(file.file)
        name = name if name != "" else os.path.splitext(file.filename)[0]

        formats = ["png" if transparent else "jpeg", "webp"]
        for format in formats:
            html_sources[format] = []

        # Resize the image to the desired width
        img_resized = img.resize((desired_width, int(desired_width * img.height / img.width)))

        # Generate and save images for each format
        image_set = []
        for format in formats:
            # Convert RGBA to RGB if saving as JPEG
            if format in ["jpg", "jpeg"] and img_resized.mode == 'RGBA':
                img_resized = img_resized.convert('RGB')

            output_filename = f"{name}.{format}"
            img_byte_arr = io.BytesIO()
            img_resized.save(img_byte_arr, format=format.upper() if format != "jpeg" else "JPEG")
            img_byte_arr.seek(0)
            image_set.append((output_filename, img_byte_arr))

            names.append(output_filename)

        html = generateSimpleHTML(names, img_resized.width, img_resized.height)

        # Compress the images into a zip file in memory
        zip_byte_arr = io.BytesIO()
        with zipfile.ZipFile(zip_byte_arr, "w") as zip:
            for filename, img_byte_arr in image_set:
                zip.writestr(filename, img_byte_arr.read())
            zip.writestr("index.html", html)
        zip_byte_arr.seek(0)

        return StreamingResponse(zip_byte_arr, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=single_image.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

@app.get("/get-sizes/")
async def get_sizes():
    """
    Get the available sizes for the image set.
    """
    return sizes