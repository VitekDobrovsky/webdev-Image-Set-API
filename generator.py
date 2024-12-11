from fastapi import UploadFile, File, HTTPException
from PIL import Image
import zipfile
import io
import os

class Image_generator:
    def __init__(self, transparent: bool, responsive: bool, max_width: int, generate_HTML: bool = True, alt="", generate_CSS: bool = True):
        
        # sizes
        self.sizes = {
        "small": 420,
        "medium": 960,
        "extra_large": 1920
        }
        self.max_width = max_width
        self.minimmum_step_size = 300
        self.responsive = responsive

        # format converting
        self.transparent = transparent
        self.available_formats = self.get_available_formats(transparent)

        # generate hml 
        self.html_sources = self.initialize_HTML_sources(self.available_formats)
        self.names = []
        self.allow_HTML_generation = generate_HTML
        self.alt = alt

        # generate css
        self.allow_CSS_generation = generate_CSS
        
    def get_available_formats(self, transparent: bool) -> list:
        """
        Get the list of available image formats based on the transparency flag
        """
        return ["png" if transparent else "jpeg", "webp"]

    def initialize_HTML_sources(self, formats: list):
        """
        Initialize the HTML sources dictionary with empty lists for each format
        """
        sources = {}

        for format in formats:
            sources[format] = []
        
        return sources

    def generate_HTML(self, available_formats: list, html_sources: dict) -> str:
        """
        Generate a responsive HTML picture element with source elements for each format and zize in an img tag
        """
        html = "<picture>"

        # Generate srcset attributes for each format in reverse order (to prioritize the last format)
        for format, sources in reversed(html_sources.items()):
            srcset = ", ".join(sources)
            html += f'<source srcset="{srcset}" type="image/{format}">'

        # Find the largest image across all formats for the img src attribute
        largest_image = max(
            html_sources[available_formats[0]],
            key=lambda x: int(x.split('-')[1].split('.')[0])
        ).split(' ')[0]

        # Generate sizes attribute based on the available sizes in html_sources
        self.sizes = ", ".join(
            f"(max-width: {int(img.split('-')[1].split('.')[0])}px) {int(img.split('-')[1].split('.')[0])}px"
            for img in sorted(
                {img for imgs in html_sources.values() for img in imgs},
                key=lambda x: int(x.split('-')[1].split('.')[0])
            )
        )

        # Generate the img tag with the largest image and sizes attribute
        html += f'<img src="{largest_image}" alt="{self.alt}" sizes="{self.sizes}">'
        html += "</picture>"
        

        return html
    
    def generate_simple_HTML(self, names: list, width: int, height: int) -> str:
        """
        Generate a simple HTML picture element with a single source element for each format and an img tag
        """
        html = "<picture>"

        # Generate a single source element for each format
        for name in names:
            format = name.split('.')[0]
            html += f'<source srcset="{name}" type="image/{format}">'
        
        # Generate the img tag with the first (largest) image in the list
        html += f'<img src="{names[0]}" alt="{self.alt}" width={width} height={height}>'

        html += "</picture>"
        return html

    def generate_CSS(self, names: list, sizes) -> str:
        """
        Generate Css for background images with media queries
        """

        # get the largest image across all formats
        filtered_formats = [name for name in names if name.split('.')[1] != "webp"]
        largest_image = max(
            filtered_formats,
            key=lambda x: int(x.split('-')[1].split('.')[0])
        )


        #{
        #    "1400": ["image-1400.jpg", "image-1400.webp"],
        #}

        image_sets = {
        }

        for size in sizes:
            image_sets[size] = [name for name in names if int(name.split('-')[1].split('.')[0]) == size]

        css = f".element {{ background-image: url('{largest_image}'); }}"

        for size in image_sets.keys():
            css += f"@media (max-width: {size}px) {{ {self.generate_simple_CSS(image_sets[size])} }}"

        return css

    def generate_simple_CSS(self, names: list) -> str:
        """
        Generate Css for background images
        """
        css = ".element { background-image: "

        for i, name in enumerate(names):
            separator = ", " if i < len(names) - 1 else ";"               
            css += f"url('{name}')" + separator
        
        css += "}"
        return css  


    def get_sizes(self, max_width: int, available_sizes: dict, min_step_size, responsive: bool) -> list:
        """
        Generate size for responsive images
        """
        sizes = []
        if responsive:
            sizes = [size for size in available_sizes.values() if size < (max_width - min_step_size)]
        sizes.append(max_width)
        return sizes
    
    def generate_zip(self, image_set: list, html: str, css: str, generate_HTML: bool = True, generate_CSS: bool = True):
        """
        Compress the images into a zip file in memory
        """
        # generate zip file
        zip_byte_arr = io.BytesIO()
        with zipfile.ZipFile(zip_byte_arr, "w") as zip:
            for filename, img_byte_arr in image_set:
                zip.writestr(filename, img_byte_arr.read())
            if generate_HTML:
                zip.writestr("index.html", html)
            if generate_CSS:
                zip.writestr("styles.css", css)
        
        zip_byte_arr.seek(0)
        return zip_byte_arr

    def generate_image_set(self, file: UploadFile = File(...), name:str = "") -> list:
        """
        Generate a set of images with different sizes and formats from the uploaded image. 
        """
        # set the name of the file (same as input filename if not provided)
        name = name if name != "" else os.path.splitext(file.filename)[0]
        img = Image.open(file.file)
        sizes = self.get_sizes(self.max_width, self.sizes, self.minimmum_step_size, self.responsive)
        
        image_set = []

        # create a list of images with different sizes and formats
        for size in sizes:
            for format in self.available_formats:
                img_resized = img.resize((size, int(size * img.height / img.width)))
                    
                # Convert RGBA to RGB if saving as JPEG
                if format in ["jpg", "jpeg"] and img_resized.mode == 'RGBA':
                    img_resized = img_resized.convert('RGB')
                
                output_filename = f"{name}-{size}.{format}"

                # save to in-memory byte array
                img_byte_arr = io.BytesIO()
                img_resized.save(img_byte_arr, format=format.upper() if format != "jpeg" else "JPEG")
                img_byte_arr.seek(0)
                image_set.append((output_filename, img_byte_arr))

                # generate HTML sources
                if self.responsive:
                    self.html_sources[format].append(f"{output_filename} {size}w")

                self.names.append(output_filename)
                
        # generate HTML and CSS
        if self.responsive:
            html = self.generate_HTML(self.available_formats, self.html_sources)
            css = self.generate_CSS(self.names, sizes)
        else:
            html = self.generate_simple_HTML(self.names, size, img_resized.height)
            css = self.generate_simple_CSS(self.names)

            

        
        # generate zip file
        zip_byte_arr = self.generate_zip(image_set, html, css, self.allow_HTML_generation, self.allow_CSS_generation)

        return zip_byte_arr
