from PIL import Image

def extract_text(image: Image.Image) -> dict:
    """Optional PaddleOCR adapter. Returns a safe manual-review status if unavailable."""
    try:
        from paddleocr import PaddleOCR
        # Instantiated only when OCR is requested; model downloads may be needed.
        engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        result = engine.ocr(image, cls=True)
        lines = []
        for block in (result or []):
            for item in (block or []):
                if len(item) >= 2 and item[1]:
                    lines.append({'text': str(item[1][0]), 'confidence': float(item[1][1])})
        return {'available': True, 'text': '\n'.join(x['text'] for x in lines), 'lines': lines, 'needs_review': any(x['confidence'] < 0.85 for x in lines)}
    except Exception as exc:
        return {'available': False, 'text': '', 'lines': [], 'needs_review': True, 'message': 'OCR işləməyib; cavabları müəllim yoxlamalıdır.', 'detail': type(exc).__name__}
