# 📋 Changelog

## [v2.0.0-alpha.8] - 2026-11-11 (Kvieta Süper Odak & Brain Map & Güvenlik/Stabilite Yamaları)

### 🎯 Kvieta Altyapısından Esinlenen Süper Odak & Konu Hakimiyeti
1. **🎯 Kvieta Süper Odak Motoru (Super Focus Engine):**
   - **Odak Niyeti Belirleme:** Seans öncesi hedef belirleme (`FocusIntention`), 15/25/45 dk süre seçenekleri.
   - **68px Hafif HUD:** Sayfa üstünde dikkat dağıtmayan ince niyet şeridi, geri sayım sayacı ve yumuşak ilerleme çubuğu.
   - **Nazik Kapanış Uyarıları:** 5 dakika ve 1 dakika kala sakinleştirici, toparlayıcı bildirimler.
   - **Oturum Kapanış Özeti:** Süre dolduğunda niyet kontrolü, okunan sayfa kaydı ve günlük ritim kütüğü.
2. **🧠 Brain Map (Konu Hakimiyet Haritası):**
   - **İnteraktif Takımyıldızı Grafiği (SVG):** Belge bölümlerine göre dinamik 6-8 konu düğümü, %75+ yeşil, %50-74 sarı, <%50 kırmızı seviye renklendirmesi.
   - **Hata Defteri Senkronizasyonu:** Çözülmemiş hataların konuya göre haritada anlık takibi.
   - **⚡ Zayıf Noktayı Pekiştir:** Zayıf konuya tıklandığında Co-Worker'ın anında 2 cümlelik özet ve tuzaklı pekiştirme sorusu sunması.
3. **📅 Günlük Çalışma Planı & Ritim Kalkanları:**
   - Sayfa okuma, odak seansı ve hata pekiştirme görevlerinin otomatik tamamlanması.
   - Ritim Kalkanları (`🛡️ 2 Kalkan`) ile yoğun günlerde serinin korunması.
4. **🛡️ Derin Güvenlik & Mantık Hata Yamaları:**
   - Bionic reading kesme işareti (`&#039;`) dilimleme rendering hatası düzeltildi.
   - İçindekiler (TOC) dropdown'ında XSS/HTML Injection açığı kapatıldı.
   - Not kopyalama butonundaki çok satırlı tırnak JS SyntaxError'ı giderildi.
   - Tüm kaynaklar silindiğinde sayfaların ekranda donuk kalması (ghost text) düzeltildi.
   - Günlük seri (streak) hesaplamasındaki çoklu gün atlama mantık hatası çözüldü.
   - Not dışa aktarımında masaüstü hedefleme ile dosya kaybolma/yetki sorunları giderildi.
   - Sayfa çıkarma hatalarında 1:1 indeks sapmasını önleyen placeholder eklendi.
   - Cambridge/Tureng gibi kısıtlı siteler için yerel OS tarayıcı açma köprüsü (`open_external_url`) eklendi.

---

## [v2.0.0-alpha.7] - 2026-11-07 (Araştırma İstasyonu & Çalışma Hızlandırıcıları)

### 🌐 Araştırma İstasyonu & Akademik Hızlı Bağlantılar
- **Kayar Yan Panel:** Çalışma masasından ayrılmadan Tureng, Cambridge Dictionary, Desmos, Wikipedia ve DuckDuckGo ile anında akademik araştırma.
- **Seçilen Metinden Tek Tıkla Arama:** Kitapta seçilen herhangi bir ifadeden araştırma paneline aktarım.

### 🚀 Çalışma Hızlandırıcıları (Accelerators)
- **🔤 Bionic Reading:** Kelimelerin ilk %45'lik harflerini vurgulayarak göz atlamasını ve odak hızını 2 kat artıran okuma modu.
- **🃏 3D Hafıza Kartları (Flashcards):** Gerçek 3D kart döndürme animasyonu (`preserve-3d`) ve Hata Defteri'ndeki yanlışlardan otomatik kart türetme.
- **🔊 Sesli Okuma (TTS):** Metin ve çözümleri doğal Türkçe ve İngilizce telaffuzla okuyan Web Speech entegrasyonu.
- **🎯 Sınav Geri Sayım HUD:** Karşılama ekranında hedeflenen sınav tarihine kalan gün ve sayfa sayacı.

---

## [v2.0.0-alpha.6] - 2026-11-07 (Apple Books & Arc & Raycast Yeni Nesil Arayüz Devrimi)

### 🌟 11 Yeni Nesil Görsel ve Etkileşimsel Özellik
1. **📖 İki Sayfalı Gerçek Kitap Açılımı (Özellik 6):** Masada gerçek bir kitap gibi 2 sayfa yan yana (`Book Spread`), ortada dikiş katlanma gölgesi (`spine crease`) ve pürüzsüz sayfa geçişleri.
2. **🌙 Karanlık Mod Akıllı Kağıt Tonlaması (Özellik 7):** Gece çalışırken beyaz PDF'lerin gözü kör etmesini engelleyen Koyu Kömür (`#1c1b18`), Sıcak Sepya (`#25201a`) ve Orijinal Beyaz kağıt modları.
3. **✨ Neon Soru Blok Vurgusu (Özellik 2):** Fareyle sorunun üzerine gelindiğinde parlayan Terracotta neon çerçeve (`glow ripple`) ve tek tıkla doğrudan o soruyu odak moduna alıp çözdürme.
4. **📌 Akıllı Kenar Notu İğneleri (Özellik 3):** Notion ve Medium tarzı; sayfa kenarlarına takıldığın sorular için iliştirilen şık cam not iğneleri ve dilbilgisi ipuçları.
5. **⚡ Raycast Tarzı `Ctrl+K` Komut Paleti (Özellik 4):** Klavyeden tek tuşla açılan yarı saydam Omnibar; fare kullanmadan üniteye gitme, test başlatma ve hata defterini açma.
6. **🧘 Zen & Odaklanma Modu (Özellik 5):** `Ctrl+D` veya `F11` ile tüm panelleri ve menüleri gizleyip ekranı %100 kitaba ayıran minimalist çalışma modu.
7. **🎯 İnteraktif Soru-Cevap HUD Kartları (Özellik 8):** Duolingo ve Kahoot enerjisinde, ekranda beliren şık A/B/C/D seçenekli canlı buton kartları ve anında zümrüt/kırmızı görsel geri bildirim.
8. **🎧 Çalışma Masası Ambiyans Sesi (Özellik 9):** Web Audio API tabanlı, harici internet/dosya gerektirmeyen gerçekçi yağmur ve kütüphane odaklanma sesleri.
9. **🌌 Görsel Konu Hakimiyeti Ağı (Özellik 11):** Sıkıcı progress bar'lar yerine parlayan interaktif beceri takımyıldızı grafiği (*Grammar ➔ Tenses ➔ Present Perfect*).
10. **🪄 Seç & Açıkla Yüzen Menü (Özellik 13):** Kitapta herhangi bir metin seçildiğinde farenin tam üstünde beliren `[⚡ Çöz] [💡 İpucu] [🇹🇷 Çevir] [📌 Not Al]` baloncuğu.
11. **📑 Çoklu Sekmeli Kitap Masası (Özellik 14):** Arc Browser tarzı; üst barda dersler ve kitaplar arasında anında geçiş sağlayan yüzdelik ilerleme rozetli pinli sekmeler.

---

## [v2.0.0-alpha.5] - 2026-11-07 (Tauri v2 / Wry Modern Native Devrimi)

### 🌟 Gerçek Modern Web Arayüzü + Saf Rust Hibrit Mimarisi
- 🚀 **Tauri v2 / Wry Dönüşümü:** Egui'nin pikselli ve kutu gibi acil mod arayüzü tamamen kaldırıldı; arkasında saf Rust (`tao` + `wry`) çalışan modern webview motoruna geçildi.
- 🎨 **Kusursuz Claude & Kavita Görselliği:**
  - Tailwind CSS ile pürüzsüz koyu tema (`#141413` Obsidian & `#cc785c` Terracotta).
  - Google Newsreader serif başlıklar ve Plus Jakarta Sans modern tipografi.
  - Canlı cam paneller (`glassmorphism`), SVG simgeler, pürüzsüz animasyonlar ve responsive %100 yükseklik.
- 🚫 **Sıfır Python & Sıfır Port 8000:** Python yok, Uvicorn yok, arka planda açık kalan zombi işlemler yok. Tüm webview ve Rust iletişimi doğrudan bellek içi IPC kanalları (`window.ipc.postMessage`) üzerinden asenkron çalışır.
- 💎 **Tüm 6 Kritik Özellik Korundu & Modernleşti:**
  - 📚 **TOC Ünite Atlama:** Modern HTML açılır çekmece menüsü.
  - ⚡ **Hızlı Aksiyon Araç Çubuğu:** Şık SVG ikonlu aksiyon düğmeleri (Sayfayı Çöz, Sokratik İpucu, Çevir, Quiz, Notlara Kaydet).
  - 📕 **Hata Defterim:** Kart tasarımlı hata havuzu ve tek tıkla telafi quizi.
  - ⏱️ **Pomodoro & Sınav Simülatörü:** Üst barda canlı interaktif geri sayım sayacı widget'ı.
  - 📊 **Konu Hakimiyeti Radarı:** Renkli gradient dolgulu ilerleme çubukları (%85, %45, %35) ve zayıf nokta antrenman düğmesi.
  - 📤 **Hızlı İhraç Merkezi:** Modern modal penceresiyle panoya kopyalama ve Markdown/JSON çıktıları.

---

## [v2.0.0-alpha.4] - 2026-11-07 (Kavita & Claude Hibrit Estetiği + 6 Seçilmiş Özel Yetenek)

### 🎨 Kavita & Claude Hibrit Görsel Devrimi
- 🪟 **Siyah Boşluk Tuzağı Çözüldü (100% Full-Height Canvas):** Egui'nin scrollarea küçültme davranışı (`auto_shrink`) kapatıldı; kitap okuyucu tuvali, sol raf ve sağ panel dikeyde tam ekran dolduracak şekilde uyarlandı.
- 🔤 **Windows Native Segoe UI Tipografisi:** Sistemdeki `Segoe UI` ve `Segoe UI Bold` fontları taranarak arayüze entegre edildi. Retro pikselli font tamamen kaldırıldı; kristal netliğinde tipografi sağlandı.
- 📖 **Kavita Kitap Okuyucu Tuvali:** Sıcak koyu kömür kağıt dokusu (`#1b1a18`), 14px yuvarlatılmış köşeler, okunabilir hiyerarşik başlıklar ve sayfa altı yüzdelik ilerleme çubuğu (`Sayfa 1 / 2 • %50`).
- 🏺 **Claude Anthropic Renk Paleti:** Obsidian arka plan (`#141413`), Terracotta turuncu aksanlar (`#cc785c`), kumtaşı başlıklar (`#d4a373`) ve zümrüt başarı rozetleri.

### 🚀 6 Seçilmiş Yeni Nesil Özellik
1. 📚 **Özellik 5: Ünite & İçindekiler Hızlı Atlama Çekmecesi (TOC):**
   - Okuyucu üst araç çubuğunda açılır `📖 Ünite Atlama (TOC)` menüsü.
   - Kitaptaki üniteleri, konuları ve sayfa numaralarını listeleyip tek tıkla doğrudan ilgili sayfaya atlatır.
2. ⚡ **Özellik 6: Seç & Açıkla Hızlı Aksiyon Araç Çubuğu (Quick Action Bar):**
   - Okuyucu tuvalinin üstünde hazır aksiyon düğmeleri:
     - `🔍 Sayfayı Çöz` (Doğrudan Ödev Çözücüye aktarıp çözümü başlatır)
     - `💡 Sokratik İpucu` (Doğrudan yanıt vermeden yönlendirici ipuçları verir)
     - `🇹🇷 Türkçe Çevir & Açıkla` (Sayfa metni ve egzersizlerinin Türkçe çevirisi ve gramer özeti)
     - `🎯 Sayfadan Mini Quiz` (Sayfadaki konudan anında 3 soruluk pratik test üretir)
     - `📌 Notlara Kaydet` (Sayfayı tek tıkla o dersin Studio Notlarına alıntı olarak ekler)
3. 📕 **Özellik 7: Hata Defteri & Yanlış Havuzu (Mistake Journal):**
   - Ödev Kontrolcüde yanlış çıkan sorular gerekçeleriyle birlikte otomatik olarak bu havuza toplanır.
   - Soru, senin verdiğin yanlış cevap, doğrusu ve Türkçe analiz kartlar halinde listelenir.
   - `🎯 Hatalarımdan Quiz Yap` butonu ile Co-Worker sadece zayıf olunan sorulardan özel telafi testi hazırlar.
4. ⏱️ **Özellik 8: Sınav Simülatörü & Pomodoro Geri Sayımı (Interactive Timer):**
   - Üst bilgi çubuğunda canlı geri sayım sayacı (`⏱️ 25:00`).
   - Başlat / Duraklat (`▶` / `⏸`), Sıfırla (`🔄`), 25 dk (Pomodoro), 45 dk (Ders), 15 dk (Hızlı Test) modları.
   - Süre bittiğinde otomatik durum uyarısı.
5. 📊 **Özellik 10: Zayıf Nokta & Konu Hakimiyeti Radarı (Mastery Radar):**
   - Sol rafta her ders projesine özel konu hakimiyeti çubukları (Progress Bar: %90, %55, %40).
   - Kritik eksikler kırmızı ve sarı rozetlerle uyarılır.
   - `⚡ Zayıf Noktaları Çalıştır` düğmesiyle doğrudan eksik konuya odaklı antrenman başlatılır.
6. 📤 **Özellik 15: Hızlı İhraç Merkezi (Export Hub):**
   - Üst çubukta `📤 Dışa Aktar` penceresi:
     - 📋 Tek tıkla Cevap Anahtarını Panoya Kopyalama (WhatsApp / Discord paylaşımı için)
     - 📄 Ödev Çözümlerini Markdown (`Ders_Cozumu.md`) olarak kaydetme
     - 📕 Hata Defterini Markdown (`Hata_Defterim.md`) olarak kaydetme
     - 💾 Ders Projesini `.json` olarak yedekleme

---

## [v2.0.0-alpha.3] - 2026-11-06 (Gemini Notebook & v1 Ödev Çözücü / Kontrolcü Mimarisi)

### 🎯 v1 Klasik Özelliklerin Saf Rust'a Entegrasyonu
- ⚡ **Ödev Çözücü Studio (Homework Solver):** v1'deki tüm soru ve alıştırmaları otomatik çözme motoru doğrudan Saf Rust içine entegre edildi.
  - CEFR Dil Seviyesi seçimi: `A1`, `A2`, `B1`, `B2`, `C1`.
  - Detaylı / Açıklamalı Çözüm modu (kuralı adım adım anlatan).
  - Doğal Öğrenci Hissi (Human Touch - ~%95 başarı, doğal el yazısı hissi).
  - Tek tıkla tüm sayfa egzersizlerini çözüp düzenli Cevap Anahtarı (Answer Key) çıkarma.
- 🔍 **Ödev Kontrol Et & Puanla Motoru (Homework Checker & Grader):** Öğrencinin yazdığı kendi cevaplarını değerlendirme, tek tek doğru (`✅`) ve yanlış (`❌`) tespiti yapma.
  - Sınav Not Karnesi: `🎯 Puan: 85/100 (4 Doğru, 1 Yanlış)`.
  - Hatalı sorularda doğru cevabı ve Türkçe gerekçesini gösterme.
  - Öğretmen Tavsiyesi ve Geliştirme Notu üretme.
  - Hızlı test için tek tıkla `📝 Örnek Cevap Doldur` butonu.
- 📌 **Ders Notlarına Aktarma:** Üretilen cevap anahtarları ve karne raporları tek tıkla o dersin Studio Not Defterine kaydedilebilir.
- 📚 **Çoklu Ders Notebook'ları:** İngilizce, Kalkülüs, Fizik vb. her derse özel bağımsız proje açabilme, kaynak rafı ve grounding desteği.
- 🪶 **5.04 MB Ultra Hafif Binary:** Hem `PrepMate-2.0-Alpha-2.exe` hem `PrepMate-2.0-Alpha-3.exe` güncellendi; <30ms açılış, 0 webview, 0 python bağımlılığı.

---

## [v2.0.0-alpha.2] - 2026-11-06 (Pure Rust Native Rebirth)

### 🦀 Saf Rust & 0-Webview Dönüşümü
- ⚡ **Boyut 83.6 MB'tan 4.7 MB'a Düştü:** Python yorumlayıcısı, yüzlerce DLL ve PyInstaller ZIP paketleyicisi tamamen çöpe atıldı; tek bir 4.7 MB'lık saf Windows binary'si elde edildi (%94.3 küçülme).
- 🚀 **0.03 Saniyede Açılış (Instant Launch):** Tıkladığın salise doğrudan GPU tarafından çizilen native pencere ekrana geliyor. Bekleme, donma, ZIP açma yok.
- 🚫 **Sıfır Webview & Sıfır Port 8000:** Edge WebView2 motoru, Chromium, web sunucusu ve tarayıcı önbellek çakışmaları tamamen kaldırıldı. Arayüz doğrudan ekran kartı (`eframe / egui`) ile 144 FPS hızında çiziliyor.
- 🤖 **Doğrudan Rust Asenkron Gemini İstemcisi:** `tokio` ve `reqwest` ile doğrudan TLS üzerinden Google Gemini API'ye bağlanıp en düşük gecikmeyle sohbet akışı sağlandı.
- 🔥 **Rust Native Study Heatmap:** Sayfa zorluk ve soru istatistikleri `serde_json` ile yerel olarak işleniyor.
- 📁 **Native Windows Dosya Seçici:** `rfd` kütüphanesiyle doğrudan Windows yerel dosya penceresi entegre edildi.

---

## [v2.0.0-alpha.1] - 2026-11-06

### 🇹🇷 Yenilikler & Altyapı Modernizasyonu
- 🤖 **Co-Worker Study Partner Agent:** PDF'leri hafızasında tutan, sağ panelden açılan, SSE token-stream ile canlı sohbet eden AI çalışma arkadaşı entegre edildi.
- ⚡ **Rust Destekli Hızlandırma (orjson):** Bounding box, sayfa koordinatları ve önbellek I/O işlemleri standart kütüphaneden 10-20 kat daha hızlı çalışan Rust tabanlı `orjson` motoruna taşındı.
- 🔄 **Asenkron ve Bloklamayan Mimari:** Ağır PDF render (`render_page_image`) ve çözüm işlemleri `anyio.to_thread.run_sync` ile arka iş parçacıklarına alındı; FastAPI event-loop'unun kitlenmesi ve arayüz donmaları tamamen engellendi.
- 🛡️ **Güvenlik Yamaları (Path Traversal Fix):** `/api/download` ve `/api/download-zip` uç noktalarında rastgele dizin erişimi açığı `is_relative_to` doğrulamasıyla kapatıldı; `file_id` formatı sanitize edildi.
- 📄 **C/C++ Native PDF-to-Markdown (pymupdf4llm):** Sayfalar saliseler içinde hafif ve hatasız `README.md` formatına dönüştürülerek LLM token tüketimi ve yanıt gecikmesi düşürüldü.
- 🔥 **Çalışma Isı Haritası (Study Heatmap):** Hangi sayfalarda daha çok soru sorulduğunu ve vakit geçirildiğini gösteren aktivite takip motoru eklendi.

---

## [v1.1.3] - 2026-10-16

### 🇹🇷 Yenilikler ve Düzeltmeler
- 📊 **Kategorizasyon ve Avantaj/Dezavantaj Tabloları Çözüldü:** Kelime gruplama (örn. *Technology / Benefits / Concerns*), beyin fırtınası ve *Advantages vs Disadvantages* gibi sütun tabanlı egzersiz alanlarının atlanması tamamen düzeltildi.
- 🎯 **Akıllı Sütun Eşleştirme:** Tablo hücreleri üstlerindeki sütun başlıkları ve soru yönergesiyle otomatik eşleştirilerek kutunun içine madde imli (dash) temiz yanıtlar yazılıyor.
- 🚫 **"In pairs" ve "Watch the video" Filtre Çakışması Giderildi:** Yönergesinde video izleme veya çift çalışma geçen gerçek yazma/tablo egzersizlerinin sözlü tartışma sanılıp atlanması engellendi.
- 🔤 **Karakter ve Tip Kutusu Temizliği:** "Grammar Tip" ve "Useful Expressions" örneklerindeki üç noktalar (`...`) sahte soru sanılmıyor; font karakter encoding hataları (soru işareti `?` çıkması) önlendi.

### 🇬🇧 What's New
- 📊 **Categorization & Pros/Cons Table Solving:** Fixed skipping of column-based workbook tables (e.g., word sorting into *Technology / Benefits / Concerns*, and *Advantages vs Disadvantages* brainstorming grids).
- 🎯 **Smart Column Alignment:** Table cells are matched to their respective column headers and task prompts, filling answers neatly as dash-bulleted points.
- 🚫 **Task Format Filter Conflict Resolved:** Authentic table activities with "working in pairs" or "watch the video" are no longer falsely dismissed as oral-only discussions.
- 🔤 **Reference Ellipsis & Glyph Cleaning:** Prevented example ellipses in grammar tip boxes from triggering phantom blanks, and resolved PDF font glyph replacements.

---

## [v1.1.2] - 2026-10-12

### 🇹🇷 Yenilikler ve Düzeltmeler
- 🚫 **"Ok" Spamı ve Sahte Kutular Engellendi:** Konu anlatımı ve bilgi kutularının tablo sanılıp yüzlerce hayali çizgi üretmesi ve sayfaya "Ok" basması tamamen çözüldü.
- 🎯 **Test Sorularında Temiz Vurgu:** Çoktan seçmeli sorularda şıklar ile soru çizgilerinin üst üste binmesi önlendi, doğru şık temizce fosforlanıyor.
- 🗣️ **Speaking ve Video Alanları Korundu:** "In pairs, discuss" gibi sözlü etkinliklere hayali kutu ve yazı basılması durduruldu.
- 📏 **Hizalama İyileştirmeleri:** Soru çizgileri ve paragraf alanları ayrıldı; yazıların soruların üstünü kapatması engellendi.

### 🇬🇧 What's New
- 🚫 **No More 'Ok' Floods & Phantom Blanks:** Fixed false table detection on lecture summaries and callouts creating fake blanks and "Ok" text spam.
- 🎯 **Clean Choice Highlighting:** Multiple-choice question stems no longer collide with answer options.
- 🗣️ **Speaking & Video Task Protection:** Discussion activities are no longer cluttered with hallucinated boxes.
- 📏 **Alignment Fixes:** Separated question lines from composition areas, preventing text overlap.

---

## [v1.1.1] - 2026-10-11
- 🌍 Çift dilli arayüz desteği (TR / EN).
- 🎨 Tasarım ve rozet iyileştirmeleri.

## [v1.1.0] - 2026-10-11
- 🌙 Göz koruma modu (Parchment Mode).
- 📋 Hızlı cevap kağıdı (Cheat Sheet) ve tek tıkla pano kopyalama.
- 🔄 40 adımlı Ctrl+Z / Ctrl+Y desteği.

## [v1.0.0] - 2026-10-06
- 🚀 İlk kararlı masaüstü sürümü (WebView2 & Gemini 3.8).
