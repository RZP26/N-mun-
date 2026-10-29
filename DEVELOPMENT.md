# İnkişaf və sınaq qeydləri

## Demo addımları
1. `pip install -r requirements.txt`
2. `uvicorn app.main:app --reload`
3. `http://127.0.0.1:8000` ünvanını açın.
4. Əvvəl müəllim və qrup yaradın, tələbələri daxil edin, sonra qiymətləndirmə və sual bankı qurun.
5. `/api/grade` endpoint-i və ya UI üzərindən cavabları JSON kimi təqdim edin.
6. Nəticələr bölməsindən Excel və PDF ixrac edin.

## OCR qeydləri
PaddleOCR optional olaraq `pip install paddleocr paddlepaddle` ilə quraşdırıla bilər, lakin uyğun paket və model yükləmələri OS/Python versiyasından asılıdır. Mövcud adapterin dili və modeli konkret test blanklarına görə konfiqurasiya edilməlidir. Şəkildən yalnız mətn çıxarmaq variant seçiminin avtomatik aşkarlanması demək deyil. Standart cavab blankları üçün ayrıca OMR emalı qurulmalı və pilot məlumatlarla dəqiqlik ölçülməlidir.

## Çoxsəhifəli PDF
`/api/upload` PDF-i saxlayır, səhifə sayını müəyyən edir və səhifə emalı üçün işarə verir. Hazırkı versiya tələbə səhifələrini QR kodla avtomatik qruplaşdırmır; `/api/pages/{file_id}` hər səhifəni `unidentified` kimi qaytarır. Bu, kimliyi təxmin etməmək üçün qəsdən belədir. İstehsal tətbiqində QR/barcode dekoder və səhifələr arası tələbə kodu təkrar yoxlaması əlavə edilməlidir.

## AI açıq cavablar
`/api/open-answer-suggestion` açar söz əsaslı demo köməkçidir, generativ AI inteqrasiyası deyil. İstehsal versiyasında provayderin şərtləri, tələbə məlumatlarının xaricə ötürülməsi, prompt injection və saxlanma riskləri yoxlanmalı, AI təklifi müəllim təsdiqi olmadan yekun qiymətə çevrilməməlidir.

## İstehsal istifadəsindən əvvəl məcburi işlər
- Autentifikasiya və rol əsaslı giriş nəzarəti
- HTTPS/TLS, CSRF və təhlükəsizlik başlıqları
- Fayl saxlama üçün məxfi obyekt anbarı, virus yoxlaması və avtomatik silinmə qaydası
- Rate limit, request limit, paralel yükləmə qoruması
- Şifrələnmiş ehtiyat nüsxələr və bərpa testləri
- Müəllim düzəlişləri üçün aktor identifikasiyası ilə audit
- SQLite əvəzinə PostgreSQL və DB miqrasiyaları
- Tam OCR/OMR sınaq korpusu, tanıma dəqiqliyi və səhv nümunələrinin ölçülməsi
- Hüquqi qiymətləndirmə və təhsil müəssisəsinin təsdiq edilmiş rubrikaları
