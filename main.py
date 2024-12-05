from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import os

app = FastAPI()

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

@app.post("/resize/")
async def resize_image(width: int, height: int, file: UploadFile = File(...)):
    """
    Resize an image to fit within the specified width and height while maintaining the aspect ratio.
    """
    try:
        # Open the uploaded image
        img = Image.open(file.file)

        # Resize the image
        img_resized = img.resize((width, height))

        # Save resized image to a file
        output_path = os.path.join(output_dir, f"resized_{file.filename}")
        img_resized.save(output_path)

        return FileResponse(output_path, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

