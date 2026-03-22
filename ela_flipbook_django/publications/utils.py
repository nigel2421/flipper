import os
import fitz  # PyMuPDF
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

def generate_pdf_cover(pdf_file, size=(600, 800)):
    """
    Extracts the first page of a PDF as an image and returns a BytesIO object with JPEG data.
    """
    try:
        # Seek to beginning if file has been read
        pdf_file.seek(0)
        
        # Open PDF from stream
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if doc.page_count == 0:
            doc.close()
            return None
            
        page = doc.load_page(0)  # First page
        
        # Render page to a pixmap (using 2.0 zoom for better quality)
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert pixmap to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(BytesIO(img_data))
        
        # Convert to RGB if necessary (to save as JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Optional: Resize while maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO as JPEG
        temp_thumb = BytesIO()
        img.save(temp_thumb, format='JPEG', quality=90)
        temp_thumb.seek(0)
        
        doc.close()
        pdf_file.seek(0) # Reset stream for other potential uses
        return temp_thumb
    except Exception as e:
        print(f"Error generating PDF cover: {e}")
        return None
