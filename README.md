# 🎓 PrepMate PDF — AI Workbook & Homework Solver

Üniversite hazırlık sınıflarında ve yabancı dil okullarında hocaların verdiği 100–200 sayfalık kalın İngilizce workbook (çalışma kitabı) PDF'lerini yapay zeka ile otomatik çözen, sadece ödev verilen sayfaları seçip **Adobe Acrobat'ta elle yazılmış gibi** doğal ve kusursuz şekilde dolduran masaüstü web uygulaması.

---

## ✨ Neden PrepMate PDF?

- **🎯 Akıllı Vektör Analizi:** Sayfadaki boşlukları (`____`), çizgili kompozisyon satırlarını ve soru tiplerini doğrudan PDF'in içinden piksel piksel çıkarır.
- **⚡ Çoklu Soru Türü Desteği:**
  - **Boşluk Doldurma** (*Fill in the blanks with correct forms*)
  - **Kompozisyon & Yazma Görevleri** (*Self-introduction, person you admire, live stream vb.*)
  - **Hata Düzeltme (*Edit Section*)** — 5.8pt zarif öğretmen el yazısı stiliyle, metinle çakışmayan temiz düzeltme
  - **Seçenek & Şık Vurgulama** (*Circle / underline the correct verb*)
- **📄 Adobe Acrobat Standartları:** Çözümler PDF'in çözünürlüğünü bozmaz; orijinal dosya üzerine saf siyah Helvetica vektör metin katmanı olarak basılır (Hocanın gözünde Adobe Acrobat ile doldurulmuş gibi görünür).
- **🚀 6x Paralel İşleme & Yük Dengeleme:** Çoklu API anahtarı havuzu ile arkada 6 worker aynı anda çalışır; 30 sayfalık ödevi saniyeler içinde bitirir.
- **💾 Kalıcı Disk Önbelleği (Cache):** Bir kez çözülen sayfa yerel önbelleğe alınır; sayfayı tekrar açtığınızda veya dışa aktarırken **1 milisaniyede** yüklenir.
- **✏️ Canlı Web Editörü:**
  - Çözümleri ekranda anlık düzenleme, silme ve fareyle sürükleyip taşıma
  - Klavye kısayolları (`←` / `→` ile sayfa geçişi, `Delete` ile silme)
  - Tek tıkla `+ Metin Kutusu Ekle` ile sayfanın en üstüne ad, soyad ve numara yazabilme
  - Sayfa karşılaştırma (Tek sayfa / Çift sayfa kitap görünümü)

---

## 🚀 Hızlı Başlangıç (Windows)

### 1. Kurulum (Tek Tık)
Klasördeki **`kurulum.bat`** dosyasına çift tıklayın. Gerekli tüm kütüphaneler otomatik olarak yüklenecektir.

*(Terminalden kurmak isterseniz: `pip install -r requirements.txt`)*

### 2. Başlatma
Klasördeki **`baslat.bat`** dosyasına çift tıklayın. Tarayıcınızda otomatik olarak `http://localhost:8000` açılacaktır.

### 3. API Anahtarını Tanımlama (Arayüzden Doğrudan)
Hiçbir dosya veya kodla uğraşmanıza gerek yok:
- Uygulama açılınca sağ üst köşedeki **"🔑 AI Anahtarı Gir"** butonuna tıklayın.
- [Google AI Studio](https://aistudio.google.com/app/apikey)'dan tamamen ücretsiz aldığınız anahtarı (veya OpenRouter anahtarınızı) kutuya yapıştırıp **"Kaydet"** deyin.
- > **⚡ Turbo Hız İpucu:** Kutuya birden fazla hesaba ait anahtarları alt alta veya virgülle yapıştırabilirsiniz. PrepMate PDF otomatik olarak 6 worker havuzu oluşturur ve sayfaları 6'şar 6'şar paralel çözerek saniyeler içinde ödevi bitirir!

*(Geliştiriciler için opsiyonel: Dilerseniz `.env` dosyası oluşturup `GEMINI_API_KEY=...` olarak da tanımlayabilirsiniz).*

---

## 📖 Kullanım Adımları

1. **PDF'i Yükleyin:** Kitap PDF dosyanızı sürükleyip ekrana bırakın (veya arayüzdeki *"🎯 Örnek İngilizce Ödev ile Hemen Dene"* butonuna basın).
2. **Ödev Sayfalarını Belirleyin:** Sayfa aralığı kutusuna sadece ödev olan sayfaları yazın (Örn: `5-15` veya `9, 13, 21`).
3. **Çözdürün:** *"⚡ Sayfaları Getir ve Otomatik Çöz"* butonuna tıklayın.
4. **Düzenleyin:** Sayfaları klavyedeki ok tuşlarıyla (`←` / `→`) gezin, gerekirse cevapları fareyle kaydırın.
5. **Dışa Aktarın:** 
   - **"Sadece Ödev Sayfalarını İndir"**: Yalnızca seçtiğiniz sayfaları hocaya atmalık derli toplu tek bir PDF olarak indirir.
   - **"Tüm Kitabı İndir"**: Çözümleri orijinal kitabın içine gömer.

---

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
| :--- | :--- |
| `←` / `→` | Önceki / Sonraki sayfaya geçiş |
| `Delete` / `Backspace` | Seçili metin kutusunu sil |
| `Escape` | Seçimi kaldır / Modalı kapat |

---

## 🛡️ Gizlilik ve Güvenlik
- API anahtarlarınız ve yüklediğiniz PDF dosyaları tamamen kendi yerel bilgisayarınızda kalır.
- `.gitignore` yapılandırması sayesinde kişisel anahtarlarınız asla GitHub'a yüklenmez.
