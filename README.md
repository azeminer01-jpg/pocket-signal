# Pocket Option Live Chart Scanner

Bu layihə Pocket Option chartını brauzerin ekran paylaşımı ilə götürüb OpenAI vision modelinə göndərir və CALL / PUT / WAIT analizi qaytarır.

## Render
1. GitHub-a bu faylları yüklə.
2. Render → New Web Service → GitHub repository seç.
3. Build:
   `pip install -r requirements.txt`
4. Start:
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment:
   `OPENAI_API_KEY = sənin OpenAI API key`
   `OPENAI_MODEL = gpt-5.6-luna` (hesabında bu model əlçatandırsa; əks halda istifadə etdiyin vision modelini yaz)

## İstifadə
1. Render URL-ni HTTPS ilə aç.
2. Aktivdən məsələn `GBP/USD OTC` seç.
3. 30 seconds və ya 1 minute seç.
4. `Live Scanner başlat` bas.
5. Brauzer ekran/tab/pəncərə seçimi açanda Pocket Option chartının olduğu ekranı paylaş.
6. Scanner təxminən 1.5–3 saniyədən bir kadr göndərir.
7. Eyni CALL/PUT iki ardıcıl analizdə gəldikdə UI-də təsdiqlənmiş siqnal göstərilir. Bu yalnız səs-küy filtridir, qazanc zəmanəti deyil.

## Vacib
- Bu sistem avtomatik əməliyyat açmır.
- 30 saniyə və 1 dəqiqəlik proqnozlar çox qeyri-müəyyəndir.
- `confidence` qazanc ehtimalı deyil; modelin görüntü üzrə analitik əminliyidir.
- Chart, timeframe və indikatorlar aydın görünmürsə sistem WAIT qaytara bilər.
- Ekran paylaşımı üçün müasir HTTPS brauzeri lazımdır. Ən stabil variant adətən desktop Chrome/Edge-dir.
- Telefon brauzerində screen capture dəstəyi cihaz/brauzerdən asılı ola bilər. Pocket Option native tətbiqinin ekranını brauzerdən səssizcə oxumaq mümkün deyil; brauzer icazəsi tələb olunur.
- Pocket Option OTC aktivlərinin siyahısı və mövcudluğu dəyişə bilər.
