# Get a set of images for web development

Upload 1 image and you will receive a set of images in png/jpg, webp, and in multiple sizes for needed devices (mobile, tablet, desktop)
<br>

### Installation

```bash
pip3 install -r requirements.txt
```

<br>

### Usage

to start <b>GUI</b>, run:

```bash
python3 start.py
```

Click on "Try it out"
<img src="images/step-one.png">

Provide required information
<img src="images/step-two.png">

Download the file or see the errors under "400" code.
<img src="images/step-three.png">

<br>

### Example curl request:

start the server:

```bash
uvicorn main:app --reload
```

send a request:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate-image-set/?max_width=600&name=my-image&transparent=true' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@uploaded-image.webp;type=image/webp'
```

<br>
The API will be available at http://127.0.0.1:8000
