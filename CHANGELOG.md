# 📋 Changelog

## [v2.0.0-alpha.1] - 2026-11-16 (PrepMate 2.0 Alpha 1 — Resmi Lansman & Saf Rust Stüdyosu)

### 🌟 Devrimsel Yeni Nesil Çalışma Stüdyosu & Saf Rust Mimarisi
PrepMate, devasa Electron veya Python paketlerini geride bırakarak **saf Rust (`wry` + `tao`)** mimarisiyle baştan inşa edildi. **Yalnızca 2.4 MB** boyutunda, <30 ms anında açılan ve doğrudan işletim sistemi GPU'suyla çalışan ultra hızlı bir yerel çalışma stüdyosuna dönüştü.

---

### 🎯 1. Kvieta Süper Odak Motoru (Super Focus Engine)
Açık kaynaklı **Kvieta** projesinin sakin, cezalandırıcı olmayan ve niyet odaklı mimarisi entegre edildi:
- **Odak Niyeti Belirleme (`FocusIntention`):** Seans başlamadan önce hedefini kaydetme (*ör. "Kalkülüs Syf 12-15 integral alıştırmaları"*), 15/25/45 dk süre seçenekleri.
- **68px Hafif HUD (`SessionSurface`):** Çalışma sırasında sayfa üstünde dikkat dağıtmayan ince niyet şeridi, geri sayım sayacı ve yumuşak ilerleme çubuğu.
- **Nazik Kapanış Uyarıları (`GentleWarningPanel`):**
  - **5 dakika kala:** *"5 Dakika Kaldı 🌿 — Harika gidiyorsun. Toparlanma vakti, son soruları toparlayabilirsin."*
  - **1 dakika kala:** *"1 Dakika Kaldı ⏳ — Son bir dakika. Seansını tamamlamaya hazırlan."*
- **Oturum Kapanış Özeti (`FocusClosureModal`):** Süre bittiğinde niyet değerlendirmesi, okunan sayfa kaydı ve günlük ritim kütüğü.

---

### 🧠 2. Brain Map (Konu Hakimiyeti Takımyıldızı)
- **İnteraktif SVG Takımyıldızı:** Yüklenen ders belgesine göre dinamik 6-8 konu düğümü, %75+ yeşil (güçlü), %50-74 sarı (tekrar gerekli), <%50 kırmızı (kritik zayıf nokta).
- **Hata Defteri Senkronizasyonu:** Çözülmemiş hataların konuya göre haritada anlık takibi.
- **⚡ Zayıf Noktayı Pekiştir:** Zayıf konuya tıklandığında Co-Worker'ın anında 2 cümlelik pratik özet kural ve tuzaklı pekiştirme sorusu sunması.

---

### 📅 3. Günlük Çalışma Planı & Ritim Kalkanları
- **Üst Bar Göstergesi:** `📅 1/3 Görev • 🔥 Günlük Seri` dinamik rozeti.
- **Otomatik İlerleyen Görevler:** Sayfa okuma, Kvieta odak seansı tamamlama ve yanlış soru pekiştirme görevlerinin arka planda otomatik tiklenmesi.
- **Ritim Kalkanları (`🛡️ 2 Kalkan`):** Öğrencinin yoğun olduğu günlerde seriyi kırmayan akıllı kalkan koruması.

---

### 🌐 4. Araştırma İstasyonu (Study Browser)
- **Kayar Yan Panel:** Çalışma masasından ayrılmadan Tureng, Cambridge Dictionary, Desmos, Wikipedia ve DuckDuckGo ile anında akademik araştırma.
- **Seçilen Metinden Tek Tıkla Arama:** Kitapta seçilen herhangi bir ifadeden araştırma paneline doğrudan arama aktarımı.
- **🪟 Dış Tarayıcı Köprüsü:** Güvenlik/CORS kısıtlı siteler için Windows varsayılan tarayıcısına (`open_external_url`) tek tıkla geçiş.

---

### 🚀 5. Çalışma Hızlandırıcıları (Accelerators)
- **🔤 Bionic Reading:** Kelimelerin ilk %45'lik harflerini kalınlaştırarak (`<b>re</b>ading`) okuma ve kavrama hızını 2 kat artıran okuma modu.
- **🃏 3D Hafıza Kartları (Flashcards):** Gerçek 3D döndürme animasyonuna sahip (`preserve-3d`) soru-cevap kartları; Hata Defteri'ndeki yanlışlardan otomatik kart türetme.
- **🔊 Sesli Okuma (TTS):** Metin ve çözümleri doğal Türkçe ve İngilizce telaffuzla seslendiren Web Speech motoru.
- **🎯 Sınav Geri Sayım HUD:** Karşılama ekranında hedeflenen sınav tarihine kalan gün ve toplam hedef sayfa sayacı.

---

### 📖 6. Çift Sayfalı Editoryal Kitap Masası
- **Gerçek Kitap Açılımı (`Book Spread`):** Yan yana 2 sayfa açılımı ve ortada dikiş katlanma gölgesi (`spine crease`).
- **Akıllı Kağıt Tonlaması:** Gece gözü yormayan Koyu Kömür (`#1c1b18`), Sıcak Sepya (`#25201a`) ve Orijinal Beyaz kağıt modları.
- **⚡ Raycast Komut Paleti (`Ctrl+K`):** Klavyeden tek tuşla üniteye gitme, test başlatma ve hata defterini açma.
- **📌 Kenar Notu İğneleri:** Notion tarzı sayfa kenarlarına iliştirilen şık not iğneleri.
- **🧘 Zen Modu (`Ctrl+D` / `F11`):** Ekranı %100 kitaba ayıran minimalist odak görünümü.
- **🎧 Ambiyans Odak Sesleri:** Web Audio API ile çalışan gerçekçi yağmur ve kütüphane sesleri.

---

### 🤖 7. Akıllı Co-Worker & Çözücü Mimarisi
- **Co-Worker Study Partner:** Doküman grounding desteği, SSE canlı akış yanıtları, Sokratik ipucu modu ve tek tıkla mini quiz üretimi.
- **📕 Hata Defteri:** Yanlış yapılan soruların çözümleri ve Türkçe gerekçeleriyle otomatik havuza toplanması.
- **CEFR Dil Seviyesi Seçimi:** `A1` - `C1` aralığında ayarlanabilir kelime ve gramer zorluğu.

---

### 🛡️ 8. Güvenlik, Mantık & Stabilite Yamaları
- Bionic reading kesme işareti (`&#039;`) dilimleme rendering hatası giderildi.
- İçindekiler (TOC) dropdown'ında XSS/HTML Injection açığı kapatıldı.
- Not kopyalama butonundaki çok satırlı tırnak JS SyntaxError'ı giderildi.
- Tüm kaynaklar silindiğinde sayfaların ekranda donuk kalması (ghost text) düzeltildi.
- Günlük seri (streak) hesaplamasındaki çoklu gün atlama mantık hatası çözüldü.
- Not dışa aktarımında masaüstü hedefleme ile dosya kaybolma/yetki sorunları giderildi.
- Sayfa çıkarma hatalarında 1:1 indeks sapmasını önleyen placeholder eklendi.

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
