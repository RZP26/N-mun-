import io
from pathlib import Path
import fitz
from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 100

class UnsafeUpload(ValueError):
    pass

def validate_file(filename: str, content: bytes) -> str:
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
            with fitz.open(stream=content, filetype='pdf') as doc:
                if doc.page_count < 1 or doc.page_count > MAX_PDF_PAGES:
                    raise UnsafeUpload(f'PDF 1-{MAX_PDF_PAGES} səhifə aralığında olmalıdır.')
        except UnsafeUpload:
            raise
        except Exception as exc:
            raise UnsafeUpload('PDF oxunmur və ya zədələnib.') from exc
        return 'application/pdf'
    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise UnsafeUpload('Şəkil faylının məzmunu etibarlı deyil.') from exc
    if ext in {'.jpg', '.jpeg'} and not content.startswith(b'\xff\xd8\xff'):
        raise UnsafeUpload('JPG fayl imzası düzgün deyil.')
    if ext == '.png' and content[:8] != b'\x89PNG\r\n\x1a\n':
        raise UnsafeUpload('PNG fayl imzası düzgün deyil.')
    return 'image/jpeg' if ext in {'.jpg', '.jpeg'} else 'image/png'

def pdf_page_count(content: bytes) -> int:
    with fitz.open(stream=content, filetype='pdf') as doc:
        return doc.page_count

def pdf_pages_as_images(content: bytes, dpi: int = 180) -> list[Image.Image]:
    """Render PDF pages locally. Student identification must never be guessed."""
    rendered = []
    with fitz.open(stream=content, filetype='pdf') as doc:
        if len(doc) > MAX_PDF_PAGES:
            raise UnsafeUpload(f'PDF {MAX_PDF_PAGES} səhifədən artıqdır.')
        for page in doc:
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            with Image.open(io.BytesIO(pix.tobytes('png'))) as img:
                rendered.append(img.convert('RGB').copy())
    return rendered

def preprocess_image(image: Image.Image) -> Image.Image:
    return ImageOps.autocontrast(ImageOps.exif_transpose(image).convert('L'))
