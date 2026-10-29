# Peşə Təhsilində Elektron Qiymətləndirmə Sistemi

Azərbaycan dilində Python və FastAPI əsasında hazırlanmış minimal prototip.

## Funksiyalar
- Müəllim, tələbə və qrup qeydiyyatı
- Peşə ixtisası, modul, təlim nəticəsi və qiymətləndirmə meyarlarının qeydiyyatı
- Test sualları və cavab açarı
- JPG, PNG və PDF yükləməsi, çoxsaylı fayl dəstəyi
- Qapalı testlərin avtomatik yoxlanması
- OCR üçün seçimli PaddleOCR inteqrasiyası və qeyri-müəyyən cavabların müəllimə yönləndirilməsi
- Çoxsəhifəli PDF-in səhifələrə ayrılması
- Excel və PDF hesabatları
- Açıq cavablar üçün müəllim təsdiqli rubrika/AI təklifi
- Fayl ölçüsü və format yoxlaması, təsadüfi fayl adları, audit qeydləri

## Status
Bu layihə prototipdir. İstehsalat istifadəsindən əvvəl autentifikasiya, HTTPS, server səviyyəli məhdudiyyətlər və real sənədlərlə OCR sınaqları tələb olunur.

## Quraşdırma
Python 3.11+ tövsiyə olunur.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Brauzerdə `http://127.0.0.1:8000` açın. API sənədləri: `http://127.0.0.1:8000/docs`.

## Qovluq strukturu

```text
app/
  main.py
  database.py
  schemas.py
  services/
    grading.py
    file_processing.py
    reports.py
    ocr.py
  templates/
    index.html
storage/       # Git-ə daxil edilmir
 tests/
 requirements.txt
 .env.example
 .gitignore
```

## Təhlükəsizlik qeydləri
- Fayllar yalnız icazə verilən uzantılarla qəbul edilir, MIME imzası da yoxlanılır.
- Faylların adı UUID ilə dəyişdirilir və açıq statik qovluqdan təqdim edilmir.
- Bu minimal nümunədə autentifikasiya prod mühiti üçün tam deyil.
- Tələbə məlumatları real nümunələrlə paylaşılmamalıdır.
- OCR nəticələri avtomatik yekun qərar sayılmır; şübhəli cavablar müəllim tərəfindən yoxlanmalıdır.

## Testlər
```bash
pytest -q
```
