from PIL import Image

_ENGINE = None
_ENGINE_ERROR = None

def extract_text(image: Image.Image) -> dict:
    """Optional OCR adapter. The default model setting is only a demo; tune to answer sheets."""
    global _ENGINE, _ENGINE_ERROR
    try:
        if _ENGINE is None and _ENGINE_ERROR is None:
            from paddleocr import PaddleOCR
            # Placeholder configuration; not a promise of Azerbaijani handwriting support.
            _ENGINE = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        if _ENGINE is None:
            raise RuntimeError(_ENGINE_ERROR or 'OCR engine unavailable')
        import numpy as np
        result = _ENGINE.ocr(np.asarray(image.convert('RGB')), cls=True)
        lines = []
        for block in (result or []):
            for item in (block or []):
                if len(item) >= 2 and item[1]:
                    lines.append({'text': str(item[1][0]), 'confidence': float(item[1][1])})
        return {'available': True, 'text': '\n'.join(x['text'] for x in lines), 'lines': lines, 'needs_review': not lines or any(x['confidence'] < 0.85 for x in lines), 'notice': 'OCR dili və dəqiqliyi real blanklarla yoxlanmalıdır; bu adapter cavab dairələrini OMR kimi oxumur.'}
    except Exception as exc:
        _ENGINE_ERROR = type(exc).__name__
        return {'available': False, 'text': '', 'lines': [], 'needs_review': True, 'message': 'OCR işləməyib; cavabları müəllim yoxlamalıdır.', 'detail': type(exc).__name__}
