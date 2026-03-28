import os
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

def is_email_automation_enabled():
    """
    Returns True if the global automation toggle is enabled.
    """
    from .models import EmailConfiguration
    config = EmailConfiguration.objects.first()
    return config.is_automation_enabled if config else False

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
        pdf_file.seek(0) # Reset stream for other potential uses
        return None

def send_single_email(user, subject, template_name, context, email_type, force_manual=False):
    """
    Helper to send an individual email and log it for analytics.
    Respects the Global Email Toggle unless force_manual=True.
    """
    if not force_manual and not is_email_automation_enabled():
        return False
        
    from .models import EmailLog
    try:
        current_site = Site.objects.get_current()
        domain = current_site.domain
        site_name = current_site.name
    except Exception:
        domain = 'businessmatters.co.ke'
        site_name = 'Business Matters Africa'
    
    base_url = f"https://{domain}" if not domain.startswith('http') else domain
    
    # Create the log entry first to get the ID for tracking
    log = EmailLog.objects.create(
        user=user,
        email_type=email_type,
        subject=subject,
        status='sent'
    )
    
    # Add tracking info to context
    tracking_url = f"{base_url}/track-email-open/{log.id}/"
    context.update({
        'tracking_url': tracking_url,
        'SITE_NAME': site_name,
        'year': timezone.now().year,
        'unsubscribe_url': f"{base_url}/profile/"
    })
    
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    
    from_email = os.environ.get('DEFAULT_FROM_EMAIL', f'noreply@{domain}')
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")
        log.status = 'failed'
        log.save()
        return False

def send_publication_notifications(new_magazines=None, new_articles=None, force_manual=False):
    """
    Sends email notifications for a set of magazines and articles.
    Returns the number of publications notified.
    """
    if not force_manual and not is_email_automation_enabled():
        return 0

    if not new_magazines and not new_articles:
        return 0

    now = timezone.now()
    
    try:
        current_site = Site.objects.get_current()
        domain = current_site.domain
        site_name = current_site.name
    except Exception:
        domain = 'businessmatters.co.ke'
        site_name = 'Business Matters'
    
    base_url = f"https://{domain}" if not domain.startswith('http') else domain
    
    publications_data = []
    
    if new_magazines:
        for mag in new_magazines:
            publications_data.append({
                'title': mag.title,
                'excerpt': mag.excerpt,
                'absolute_url': f"{base_url}{mag.get_absolute_url()}",
                'image_url': f"{base_url}{mag.cover_image.url}" if mag.cover_image else None,
            })
            
    if new_articles:
        for art in new_articles:
            publications_data.append({
                'title': art.title,
                'excerpt': art.excerpt,
                'absolute_url': f"{base_url}{art.get_absolute_url()}",
                'image_url': f"{base_url}{art.cover_image.url}" if art.cover_image else None,
            })

    if not publications_data:
        return 0

    # Get subscribed users
    subscribed_users = User.objects.filter(profile__is_subscribed=True).exclude(email='')
    
    if not subscribed_users.exists():
        # Still mark as sent so we don't spam if users are added later but content is old
        if new_magazines: new_magazines.update(email_sent=True)
        if new_articles: new_articles.update(email_sent=True)
        return len(publications_data)

    # Email content
    subject = f"New on {site_name}: {publications_data[0]['title']}"
    if len(publications_data) > 1:
        subject += f" and {len(publications_data) - 1} more"

    count_sent = 0
    for user in subscribed_users:
        context = {
            'publications': publications_data,
            'user': user,
        }
        if send_single_email(user, subject, 'publications/emails/publication_notification_email.html', context, 'notification', force_manual=force_manual):
            count_sent += 1
    
    if new_magazines: new_magazines.update(email_sent=True)
    if new_articles: new_articles.update(email_sent=True)
    
    return len(publications_data)
