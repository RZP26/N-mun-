import pytest
from app.services.file_processing import validate_file, UnsafeUpload


def test_rejects_unknown_extension():
    with pytest.raises(UnsafeUpload):
        validate_file('test.exe', b'MZ fake')


def test_rejects_fake_pdf():
    with pytest.raises(UnsafeUpload):
        validate_file('test.pdf', b'not a pdf')


def test_rejects_empty_file():
    with pytest.raises(UnsafeUpload):
        validate_file('empty.png', b'')
