# 📋 Changelog (Değişiklik Günlüğü)

Tüm önemli güncellemeler ve sürüm notları bu dosyada belgelenir.
All notable changes and release notes are documented in this file.

---

## [v1.1.2] - 2026-10-12

### 🇹🇷 Türkçe (Yenilikler ve Düzeltmeler)
- **🛡️ Sahte Tablo ve Bilgi Kutusu Filtreleme:**
  - Konu anlatım tabloları, gramer özetleri ve kenarlıksız çoktan seçmeli ızgaralarının tablo zannedilip yüzlerce hayali boşluk üretmesi engellendi.
  - Sadece gerçek egzersiz tabloları (`complete the table`, `fill in the gaps`, numaralandırılmış satırlar vb.) algılanacak şekilde sıkı doğrulama getirildi.
  - Hücre koordinatları tahmini bölme yerine doğrudan vektörel hücre sınırlarından milimetrik olarak hesaplanıyor.
- **🚫 "Ok" Flood & Placeholder Engelleme:**
  - Sayfadaki kutulara yapay zekanın "Ok", "ok.", "N/A", "None" gibi anlamsız doldurma metinleri basması hem prompt hem de PDF dışa aktarma (export) aşamasında tamamen filtrelendi.
- **🎯 Çoktan Seçmeli (Multiple Choice) Çakışma Düzeltmesi:**
  - Soru kökünde yer alan alt çizgiler (`______`) ile şık işaretlemelerinin çakışması önlendi. Soru köküne sıkışık metin basmak yerine doğrudan doğru şık fosforlu vurgu ile işaretleniyor.
- **🗣️ Sözlü / Tartışma (Speaking & Video) Koruması:**
  - "In pairs, discuss", "talk to your partner", "watch the video" gibi yazılı yanıt gerektirmeyen sözlü egzersizlere yapay zekanın linkler veya metinlerin üzerine hayali kutular uydurması (`vision fallback`) engellendi.
- **📏 Soru Çizgileri ve Essay Alanı Ayrımı:**
  - Soru işaretiyle biten veya çok satırlı soru çizgilerinin kompozisyon/paragraf alanı sanılarak uzun özet metinlerle soruların üstünü örtmesi düzeltildi.

---

### 🇬🇧 English (Release Notes)
- **🛡️ Authentic Table & Callout Filtering:**
  - Prevented grammar summaries, lecture reference tables, and borderless multiple-choice grids from being misclassified as fill-in exercise tables.
  - Added strict heuristics requiring authentic exercise markers (`complete the table`, numbered items, explicit Q&A headers) and exact cell bounding boxes.
- **🚫 "Ok" Flood & Placeholder Cleanup:**
  - Eliminated "Ok", "ok.", "N/A", and placeholder text responses across both the hybrid solver and final PDF export rendering pipeline.
- **🎯 Multiple-Choice Stem Collision Fix:**
  - Underlines (`______`) inside multiple-choice question stems no longer collide with option highlights. The system now strictly highlights the correct answer choice.
- **🗣️ Oral & Video Task Guardrails:**
  - Discussion, pairing, and video-only exercises ("discuss in pairs", "watch the video") are now preserved without hallucinating text boxes over page links or figures.
- **📏 Question Underline vs. Essay Line Distinction:**
  - Underlined questions ending with `?` are properly distinguished from open-ended composition lines, eliminating passage text overlaps.

---

## [v1.1.1] - 2026-10-11
- **🌍 Çift Dilli Arayüz (Bilingual UI):** Türkçe ve İngilizce tek tıkla dinamik dil değiştirme desteği.
- **🎨 Tasarım İyileştirmeleri:** Üst bilgi rozetleri ve Obsidian / Terracotta editoryal tema cilalamaları.
- **📦 Taşınabilir Yapı:** PyInstaller bağımlılık optimizasyonları ve tek tıkla masaüstü çalıştırma desteği.

---

## [v1.1.0] - 2026-10-11
- **🌙 Parchment (Gece / Göz Koruma) Modu:** Gece ders çalışırken beyaz PDF parlamasını kıran yumuşak sıcak kağıt filtresi.
- **📋 Hızlı Cevap Kağıdı (Cheat Sheet):** Numaralandırılmış cevapların tek tıkla panoya kopyalanabildiği kompakt modal.
- **📸 Tek Tıkla Resim Kopyalama:** Çözülen sayfayı yüksek çözünürlükte panoya kopyalama (`Ctrl+V` ile Discord/WhatsApp'a yapıştırma).
- **🔄 40 Adımlı Geri Al / İleri Al:** Kapsamlı `Ctrl+Z` ve `Ctrl+Y` geçmiş desteği.

---

## [v1.0.0] - 2026-10-06
- **🚀 İlk Kararlı Sürüm (Initial Release):**
  - Akıllı el yazısı fontları (Caveat, Indie Flower, Kalam, Patrick Hand).
  - Vektörel Acrobat PDF dışa aktarma.
  - Gemini 3.8 Flash & OpenRouter AI motoru entegrasyonu.
  - Masaüstü WebView2 uygulaması (`PrepMate-PDF.exe`).
