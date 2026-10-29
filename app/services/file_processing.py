import io
import fitz
from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 100

class UnsafeUpload(ValueError):
    pass

def validate_file(filename: str, content: bytes) -> str:
    from pathlib import Path
    ext = Path(filename or '').suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsafeUpload('Yalnız JPG, PNG və PDF qəbul edilir.')
    if not content:
        raise UnsafeUpload('Boş fayl yüklənib.')
    if len(content) > MAX_UPLOAD_BYTES:
        raise UnsafeUpload('Fayl 15 MB limitini keçir.')
    if ext == '.pdf':
        if not content.startswith(b'%PDF-'):
            raise UnsafeUpload('Faylın PDF imzası düzgün deyil.')
        try:
            doc = fitz.open(stream=content, filetype='pdf')
            if doc.page_count < 1 or doc.page_count > MAX_PDF_PAGES:
                raise UnsafeUpload(f'PDF 1-{MAX_PDF_PAGES} səhifə aralığında olmalıdır.')
            doc.close()
        except UnsafeUpload:
            raise
        except Exception as exc:
            raise UnsafeUpload('PDF oxunmur və ya zədələnib.') from exc
        return 'application/pdf'
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise UnsafeUpload('Şəkil faylının məzmunu etibarlı deyil.') from exc
    signature = content[:8]
    if ext in {'.jpg', '.jpeg'} and not content.startswith(b'\xff\xd8\xff'):
        raise UnsafeUpload('JPG fayl imzası düzgün deyil.')
    if ext == '.png' and signature != b'\x89PNG\r\n\x1a\n':
        raise UnsafeUpload('PNG fayl imzası düzgün deyil.')
    return 'image/jpeg' if ext in {'.jpg', '.jpeg'} else 'image/png'

def pdf_page_count(content: bytes) -> int:
    with fitz.open(stream=content, filetype='pdf') as doc:
        return doc.page_count

def pdf_pages_as_images(content: bytes, dpi: int = 180) -> list[Image.Image]:
    """Render PDF pages locally. OCR/identification should never guess student identity."""
    with fitz.open(stream=content, filetype='pdf') as doc:
        if len(doc) > MAX_PDF_PAGES:
            raise UnsafeUpload(f'PDF {MAX_PDF_PAGES} səhifədən artıqdır.')
        return [Image.open(io.BytesIO(page.get_pixmap(dpi=dpi, alpha=False).tobytes('png'))).convert('RGB') for page in doc]

def preprocess_image(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert('L')
    image = ImageOps.autocontrast(image)
    return image
