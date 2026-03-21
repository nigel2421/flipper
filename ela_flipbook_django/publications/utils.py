import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def resize_image_to_square(image_field, size=500):
    """
    Crops an image to a square and resizes it to the specified size.
    Modify the in-memory file so super().save() writes the resized version.
    """
    if not image_field:
        return

    try:
        # Open the image using Pillow
        img = Image.open(image_field)
        
        # Check if already square and of the right size
        if img.width == size and img.height == size:
            return

        # Calculate crop (center crop)
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2

        img = img.crop((left, top, right, bottom))
        
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
            
        img = img.resize((size, size), resample=resample)

        # Save back to a BytesIO object
        temp_thumb = BytesIO()
        img_format = img.format if img.format else 'JPEG'
        if img_format == 'MPO':
            img_format = 'JPEG'
            
        img.save(temp_thumb, format=img_format, quality=90)
        temp_thumb.seek(0)
        
        # Update the field's file attribute with the new content
        # We use ContentFile so super().save() handles the writing to storage
        new_name = os.path.basename(image_field.name)
        image_field.file = ContentFile(temp_thumb.read(), name=new_name)
        
    except Exception as e:
        print(f"Error resizing image: {e}")
