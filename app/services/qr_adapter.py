"""Optional QR decoder. Install opencv-python-headless to enable it."""

def decode_student_qr(image):
    """Return a decoded code, or require manual review when no code is found."""
    try:
        import cv2
        import numpy as np
        detector = cv2.QRCodeDetector()
        arr = np.asarray(image.convert('RGB'))[:, :, ::-1].copy()
        value, points, _ = detector.detectAndDecode(arr)
        value = (value or '').strip()
        return {'student_code': value or None, 'status': 'decoded' if value else 'not_found', 'needs_review': not bool(value)}
    except Exception as exc:
        return {'student_code': None, 'status': 'unavailable', 'needs_review': True, 'message': type(exc).__name__}
