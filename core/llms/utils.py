## supporting functions
import base64, io
from typing import Any, Union, List
from PIL import Image  # Pillow image library

# thanks to https://community.openai.com/t/how-to-load-a-local-image-to-gpt4-vision-using-api/533090/5

def resize_image(image, max_dimension):
    width, height = image.size

    # Check if the image has a palette and convert it to true color mode
    if image.mode == "P":
        if "transparency" in image.info:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
    return image

def convert_to_png(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

def create_image_content(image):
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image}"}
    }




def get_attr(attr:str, kwargs:dict, cls:Any=None) -> Any:
    attribute = kwargs.get(attr, None) if kwargs else None
    if (attribute is None) and (cls is not None):
        if hasattr(cls, attr):
            attribute = getattr(cls, attr)
    return attribute



def process_image(image: Union[str, Image.Image], max_size: int) -> str:
    if isinstance(image, str):
        with Image.open(image) as img:
            return process_pillow_image(img, max_size)
    elif isinstance(image, Image.Image):
        return process_pillow_image(image, max_size)
    else:
        raise ValueError("Input must be either a file path (str) or a Pillow Image object")


def process_pillow_image(image: Image.Image, max_size: int) -> str:
    width, height = image.size
    mimetype = image.get_format_mimetype() if hasattr(image, 'get_format_mimetype') else "image/png"
    
    if mimetype == "image/png" and width <= max_size and height <= max_size:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    else:
        resized_image = resize_image(image, max_size)
        png_image = convert_to_png(resized_image)
        return base64.b64encode(png_image).decode('utf-8')

def user_message_with_images(
    user_msg_str: str,
    images: List[Union[str, Image.Image]]|None = None,
    max_size_px: int = 1024,
) -> dict:
    if images is None:
        images = []
    
    base64_images = [process_image(img, max_size_px) for img in images]

    content = [{"type": "text", "text": user_msg_str}]
    content += [create_image_content(image) for image in base64_images]
    
    return {"role": "user", "content": content}
