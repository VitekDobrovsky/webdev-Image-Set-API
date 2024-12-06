# Get a set of images for web development

Upload 1 image and you will receive a set of images in png/jpg, webp, and in multiple sizes for needed devices (mobile, tablet, desktop)
<br>

### Installation

```bash
pip install fastapi uvicorn pillow
```

if this doesn't work, try:

```bash
pip3 install fastapi uvicorn pillow
```

<br>

### Usage

run

```bash
uvicorn main:app --reload
```

and go to: http://127.0.0.1:8000/docs#/default/generate_image_set_generate_image_set__post

<br>

### Example curl request:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate-image-set/?max_width=600&name=my-image&transparent=true' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@uploaded-image.webp;type=image/webp'
```

<br>
The API will be available at http://127.0.0.1:8000
