# 🎓 Ödevmatik AI — Adobe Acrobat Stili Akıllı Ödev Çözücü

Üniversite hazırlık ve yabancı dil okullarında hocaların verdiği 100–200 sayfalık kalın İngilizce workbook (çalışma kitabı) PDF'lerini otomatik olarak çözen, sadece ödev verilen sayfaları seçip **Adobe Acrobat'ta elle yazılmış gibi** doğal ve kusursuz şekilde dolduran masaüstü web uygulaması.

---

## ✨ Özellikler

- **🎯 Akıllı Vektör Tespiti:** Sayfadaki boşlukları (`____`), çizgili kompozisyon satırlarını ve soru yapılarını doğrudan PDF'in içinden milimetrik koordinatlarla çıkarır.
- **⚡ Çoklu Soru Türü Desteği:**
  - Boşluk Doldurma (*Fill in the blanks*)
  - Paragraf & Kompozisyon Yazma (*Self-introduction, person you admire vb.*)
  - Hata Düzeltme (*Edit / Read the paragraph and correct errors*) — 5.8pt zarif öğretmen düzeltmesi
  - Şık & Seçenek Vurgulama (*Circle/underline the correct option*)
- **📄 Adobe Acrobat Standartları:** Çözümler PDF'in çözünürlüğünü bozmaz; orijinal dosya üzerine saf siyah Helvetica vektör metin katmanı olarak basılır.
- **🚀 6x Paralel İşleme & Yük Dengeleme:** Birden fazla API anahtarı girildiğinde eşzamanlı worker'larla dakikalar süren ödevleri saniyeler içinde çözer.
- **💾 Kalıcı Disk Önbelleği (Cache):** Bir kez çözülen sayfa diske kaydedilir; sayfayı tekrar açtığınızda veya PDF dışa aktarırken **1 milisaniyede** yüklenir.
- **✏️ Canlı Web Editörü:**
  - Çözümleri ekranda anlık düzenleme, silme ve fareyle sürükleyip taşıma
  - Üste ad, soyad, öğrenci numarası eklemek için `+ Metin Kutusu Ekle`
  - Sayfa karşılaştırma (Tek sayfa / Çift sayfa kitap görünümü)

---

## 🚀 Hızlı Başlangıç (Windows)

### 1. Kurulum
Klasördeki **`kurulum.bat`** dosyasına çift tıklayın. Gerekli kütüphaneler otomatik olarak yüklenecektir.

*(Terminalden kurmak isterseniz:)*
```bash
pip install -r requirements.txt
```

### 2. API Anahtarı Tanımlama
Klasördeki `.env.example` dosyasının adını `.env` olarak değiştirin ve içine API anahtarınızı yapıştırın:
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

## 📖 Kullanım Kılavuzu

1. **PDF'i Yükleyin:** Kitap PDF dosyanızı sürükleyip ekrana bırakın.
2. **Ödev Sayfalarını Belirleyin:** Sayfa aralığı kutusuna sadece ödev olan sayfaları yazın (Örn: `5-15` veya `9, 13, 21`).
3. **Çözdürün:** *"⚡ Sayfaları Getir ve Otomatik Çöz"* butonuna tıklayın.
4. **Düzenleyin:** Gerekirse cevapları fareyle kaydırın veya çift tıklayarak düzeltin.
5. **Dışa Aktarın:** 
   - **"Sadece Ödev Sayfalarını İndir"**: Yalnızca seçtiğiniz sayfaları hocaya atmalık derli toplu PDF yapar.
   - **"Tüm Kitabı İndir"**: Çözümleri orijinal kitabın içine gömer.

---

## 🛡️ Gizlilik ve Güvenlik
- API anahtarlarınız ve yüklediğiniz PDF dosyaları tamamen kendi yerel bilgisayarınızda kalır.
- `.gitignore` yapılandırması sayesinde kişisel anahtarlarınız asla GitHub'a yüklenmez.
