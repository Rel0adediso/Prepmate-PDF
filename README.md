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

*(Terminalden kurmak isterseniz:)*
```bash
pip install -r requirements.txt
```

### 2. API Anahtarı Tanımlama
Klasördeki `.env.example` dosyasının adını `.env` olarak değiştirin ve içine anahtarınızı yapıştırın:
```env
# Google AI Studio'dan tamamen ücretsiz alabilirsiniz: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSy...

# veya OpenRouter kullanmak isterseniz:
OPENROUTER_API_KEY=sk-or-v1-...
```
> **İpucu:** Birden fazla Gemini anahtarını virgülle ayırarak (`key1, key2, key3`) yazabilirsiniz. Sistem kotanız doldukça otomatik olarak diğer hesaba geçer ve 6 sayfayı aynı anda paralel çözer!

### 3. Çalıştırma
Klasördeki **`baslat.bat`** dosyasına çift tıklayın. Tarayıcınızda otomatik olarak `http://localhost:8000` açılacaktır.

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
