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

## 🚀 Kurulum ve Çalıştırma (Adım Adım)

### 0. Ön Gereksinim (Python)
Bilgisayarınızda **Python 3.10 veya daha yenisi** kurulu olmalıdır.
> ⚠️ **Önemli:** Python'ı kurarken kurulum ekranının en altındaki **"Add python.exe to PATH"** kutucuğunu MUTLAKA işaretleyin.

---

### 1. Projeyi İndirin
- Bu sayfadaki yeşil **`Code`** butonuna tıklayıp **`Download ZIP`** deyin ve inen zip dosyasını bir klasöre çıkartın.
- *(Veya Git ile: `git clone https://github.com/Rel0adediso/Prepmate-PDF.git`)*

---

### 2. Kurulum (Tek Tık)
Klasör içindeki **`kurulum.bat`** dosyasına çift tıklayın. Gerekli tüm kütüphaneler (`fastapi`, `pymupdf`, `google-genai` vb.) otomatik kurulacaktır.

*(Terminalden kurmak isterseniz: `pip install -r requirements.txt`)*

---

### 3. Çalıştırma
Klasör içindeki **`baslat.bat`** dosyasına çift tıklayın. Tarayıcınızda otomatik olarak `http://localhost:8000` açılacaktır.

---

### 4. API Anahtarını Tanımlama
İki farklı şekilde kolayca tanımlayabilirsiniz:

#### Yöntem A: Arayüzden Doğrudan (En Kolayı - Kodsuz)
1. Uygulama açılınca sağ üst köşedeki **"🔑 AI Anahtarı Gir"** butonuna tıklayın.
2. [Google AI Studio](https://aistudio.google.com/app/apikey)'dan tamamen ücretsiz aldığınız anahtarı kutuya yapıştırıp **"Kaydet"** deyin.
3. > **⚡ 6x Turbo Paralel Hız:** Kutuya birden fazla hesaba ait anahtarları alt alta veya virgülle yapıştırırsanız, PrepMate PDF 6 worker havuzu oluşturur ve sayfaları 6'şar 6'şar paralel çözerek saniyeler içinde ödevi bitirir!

#### Yöntem B: Dosya ile (.env)
Klasördeki **`.env.example`** dosyasının adını **`.env`** olarak değiştirin ve içine anahtarınızı yapıştırın:
```env
# Ücretsiz almak için: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSy1..., AIzaSy2...

# veya OpenRouter:
OPENROUTER_API_KEY=sk-or-v1-...
```

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
