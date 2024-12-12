from generator import Image_generator
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import os
import io

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Set Generator API"}

@app.post("/generate/")
async def generate_image_set(max_width: int, image: UploadFile = File(...), image_name: str = "", multiple_sizes: bool = True, transparent: bool = False, generate_HTML: bool = True, alt:str = "", generate_CSS: bool = True):
    """
    Generate a set of images with different sizes and formats from the uploaded image. \n
    NOT RECOMMENDED FOR IMAGE UPSCALING!!!
    """
    try:
        zip = Image_generator(transparent, multiple_sizes, max_width, generate_HTML, alt, generate_CSS).generate_image_set(image, image_name)
        return StreamingResponse(io.BytesIO(zip.read()), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=image_set.zip"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")