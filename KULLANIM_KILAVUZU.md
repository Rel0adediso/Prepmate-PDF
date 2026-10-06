# 🎓 Ödevmatik AI - Adobe Acrobat Stili Ödev Doldurucu

Hocaların verdiği 100-200 sayfalık İngilizce kitap/workbook PDF'lerinden sadece ödev verilen sayfaları seçip, soruları otomatik çözdürerek **Adobe Acrobat'ta kendin yazmışsın gibi** dolduran ve dışa aktaran yerel masaüstü aracı.

---

## 🚀 Nasıl Başlatılır?

1. Klasördeki **`baslat.bat`** dosyasına çift tıklayın.
2. Otomatik olarak sunucu çalışır ve tarayıcınızda **`http://localhost:8000`** açılır.

*(Veya terminalden başlatmak isterseniz: `python -m uvicorn app:app --port 8000`)*

---

## ⚡ Kullanım Adımları

1. **PDF'i Yükle:**
   - 150 sayfalık ders kitabını veya ödev föyünü ekrana sürükleyip bırak.
2. **Ödev Sayfalarını Belirle:**
   - Sayfa aralığı kutusuna hocanın verdiği sayfaları yaz (Örn: `15-20` veya `14, 15, 18`).
   - Sistem tüm kitabı değil, **sadece bu sayfaları** işleyerek hem hızlı sonuç verir hem de kotanı korur.
3. **API Anahtarı (İlk Seferde):**
   - Sağ üstteki `Gemini API Anahtarı` butonuna tıkla.
   - [Google AI Studio](https://aistudio.google.com/app/apikey)'dan aldığın ücretsiz anahtarı yapıştır ve "Kaydet"e bas (Tarayıcı hatırlar, her seferinde sormaz).
4. **"⚡ Sayfaları Getir ve Otomatik Çöz" Butonuna Bas:**
   - Gemini Vision sayfadaki boşlukları (`____`), test şıklarını ve açık uçlu soruları bulur.
   - Doğru cevapları tam boşluk çizgilerinin üzerine **Adobe Acrobat stili (Helvetica, dümdüz siyah)** metin olarak yerleştirir.
5. **Acrobat Önizleme ve Canlı Düzenleme:**
   - Ekranda sayfayı görürsün.
   - Bir kutuyu fareyle tutup kaydırabilir, içine tıklayıp metni değiştirebilir veya boyutu (9pt-14pt) ayarlayabilirsin.
   - **`+ Metin Kutusu Ekle`** ile en üste adını, numaranı veya istediğin notu ekleyebilirsin.
6. **PDF'i İndir (İki Seçenek):**
   - 📄 **"Sadece Ödev Sayfalarını İndir"**: Sadece çözdüğün 5 sayfayı hocaya atmalık tertemiz tek bir PDF olarak indirir.
   - 📚 **"Tüm Kitabı İndir"**: Orijinal 150 sayfalık kitabın içine çözümleri gömüp tüm kitabı indirir.

---

## 🛠️ Teknik Özellikler
- **Orijinal Düzen Korunur:** PDF yeniden çizilmez; orijinal dosya üzerine Acrobat annotation/text katmanı olarak basılır (Sıfır çözünürlük/kalite kaybı).
- **Adobe Acrobat Standart Yazı Tipi:** `helv` (Helvetica) ve saf siyah (`#000000`).
- **Hafif & Hızlı:** FastAPI + PyMuPDF arka planı ile saniyeler içinde çalışır.
