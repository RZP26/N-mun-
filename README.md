# Peşə Təhsilində Elektron Qiymətləndirmə Sistemi

Azərbaycan dilində Python və FastAPI əsaslı prototip. Peşə təhsilində modul, təlim nəticəsi və qiymətləndirmə meyarı kontekstini qoruyaraq qapalı testləri yoxlamaq, skan olunmuş işləri yükləmək və hesabat hazırlamaq üçün nəzərdə tutulub.

## Funksiyalar
- Müəllim, ixtisas qrupu və tələbə siyahısı
- Modul, təlim nəticəsi və qiymətləndirmə meyarı ilə qiymətləndirmə kartı
- Test sualları və cavab açarı
- JPG/JPEG, PNG, PDF, bir neçə faylın birlikdə yüklənməsi
- Fayl ölçüsü, uzantı, fayl imzası və məzmun yoxlaması; UUID adı ilə storage-a yazma
- Qapalı test cavablarının avtomatik yoxlanması
- Seçimli PaddleOCR adapteri, aşağı inamlı tanımanın müəllimə qaytarılması
- PDF səhifə sayının müəyyən edilməsi və səhifələri şəkilə çevirmə xidməti
- Excel və PDF nəticə hesabatları
- Açıq cavablar üçün rubrika köməkçisi; yekun qiyməti müəllim təsdiq edir
- Qiymət düzəlişlərinin audit qeydləri
- Nümunə testlər

## Quraşdırma
Python 3.11 tövsiyə olunur.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Sonra `http://127.0.0.1:8000` açın. API sənədləri `http://127.0.0.1:8000/docs` ünvanındadır.

## İlk sınaq
1. «Müəllim və qruplar» bölməsində müəllim, qrup və tələbə əlavə edin.
2. «Test və cavab açarı» bölməsində qiymətləndirmə yaradın.
3. Eyni bölmədə sualları və düzgün cavabları əlavə edin.
4. «Cavabları yoxla» bölməsində, məsələn, `{"1":"B","2":"DOĞRU","3":"UNCERTAIN"}` daxil edin.
5. «Hesabatlar» bölməsindən Excel və PDF fayllarını endirin.

## OCR
Əsas quraşdırmada OCR kitabxanası məcburi deyil. PaddleOCR ayrıca quraşdırıla bilər:

```bash
pip install paddleocr paddlepaddle
```

PaddleOCR versiyasının Python və platformaya uyğunluğu yoxlanmalıdır. Bu prototipdə OCR mətn çıxarma adapteridir; A/B/C/D dairələrini avtomatik seçən tam OMR sistemi hələ əlavə olunmayıb. Azərbaycan dilində əl yazısı üçün real skanlar üzərində sınaq lazımdır.

## Toplu PDF
Bir PDF faylı bir neçə tələbənin səhifələrini qəbul edir və səhifə sayı müəyyən edilir. Hazırkı prototip tələbə adını və QR kodunu özü güman etmir. Tələbə işlərinin QR kod əsasında avtomatik bölünməsi ayrıca növbəti mərhələdir.

## AI dəstəyi
Açıq cavab köməkçisi hazırda demo açar-söz müqayisəsidir, generativ AI provayderinə bağlı deyil və yekun bal vermir. İstehsal versiyasında API açarı server sirri kimi saxlanmalı, məlumatların xaricə ötürülməsi hüquqi və məxfilik baxımından qiymətləndirilməli, müəllim təsdiqi saxlanmalıdır.

## Testlər
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Təhlükəsizlik və məhdudiyyətlər
Bu minimal prototip istehsal sisteminin hazır olduğu anlamına gəlmir. Autentifikasiya və rollar, HTTPS, rate limit, antivirus skanı, məxfi fayl anbarı, şifrələnmiş ehtiyat nüsxələr, PostgreSQL və hüquqi uyğunluq yoxlaması əlavə edilməlidir. Geniş istifadədən əvvəl OCR/OMR dəqiqliyini real və icazəli test dəsti ilə yoxlayın.
