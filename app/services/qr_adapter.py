"""Optional QR code adapter. Installs opencv-python-headless separately."""

def decode_student_qr(image):
    """Return decoded QR payload or None; missing/ambiguous codes require review."""
    try:
        import cv2
        import numpy as np
        detector = cv2.QRCodeDetector()
        array = np.asarray(image.convert('RGB'))[:, :, ::-1].copy()
        value, points, _ = detector.detectAndDecode(array)
        value = (value or '').strip()
        return {'student_code': value or None, 'status': 'decoded' if value else 'not_found', 'needs_review': not bool(value)}
    except Exception as exc:
        return {'student_code': None, 'status': 'unavailable', 'needs_review': True, 'message': type(exc).__name__}
