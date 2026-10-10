# 🎓 PrepMate PDF — AI Workbook & Homework Solver

[![⬇️ WINDOWS PROGRAMINI İNDİR (.EXE)](https://img.shields.io/badge/⬇️_WINDOWS_İÇİN_İNDİR_(.EXE)-v1.0.2_Hazır-6366f1?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Rel0adediso/Prepmate-PDF/releases/latest)
[![Sürüm](https://img.shields.io/badge/Sürüm-v1.0.2-10b981?style=for-the-badge&logo=github)](https://github.com/Rel0adediso/Prepmate-PDF/releases)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-3b82f6?style=for-the-badge)](#)

> 🚀 **HİÇBİR ŞEY BİLMEYENLER İÇİN 10 SANİYEDE BAŞLATMA:**  
> 1. Yukarıdaki **[⬇️ WINDOWS İÇİN İNDİR (.EXE)](https://github.com/Rel0adediso/Prepmate-PDF/releases/latest)** butonuna basıp **`PrepMate-PDF.exe`** dosyasını indirin.  
> 2. İnen dosyaya **çift tıklayın**. Program masaüstü penceresi olarak anında açılacaktır!  
> *(Bilgisayarınızda Python olmasına, ZIP çıkarmaya veya kod çalıştırmaya gerek yoktur).*

---

Üniversite hazırlık sınıflarında ve yabancı dil okullarında hocaların verdiği 100–200 sayfalık kalın İngilizce workbook (çalışma kitabı) PDF'lerini yapay zeka ile otomatik çözen, sadece ödev verilen sayfaları seçip **Adobe Acrobat'ta elle yazılmış gibi** doğal ve kusursuz şekilde dolduran masaüstü web uygulaması.

---

## ✨ Neden PrepMate PDF?

- **🎯 Akıllı Vektör & Şablon Analizi:** Sayfadaki boşlukları (`____`), çizgili kompozisyon satırlarını, tabloları ve diyagramları doğrudan PDF'in vektörel yapısından piksel piksel çıkarır.
- **⚡ Çoklu Soru & Diyagram Türü Desteği:**
  - **Boşluk Doldurma:** (*Fill in the blanks with correct forms*)
  - **Zihin Haritaları & Sunburst:** (*Spider diagrams / mind-maps, dairesel beyin fırtınası kolları*)
  - **Beyin Fırtınası Liste Şablonları:** (*Brainstorming listing templates 1-10*)
  - **Kompozisyon & Paragraf Kutuları:** (*Your Paragraph, Unit Task, açık uçlu yazma kutuları*)
  - **Fiil-İsim Eşleştirmeleri:** (*Collocations: pack a suitcase, check weather vb.*)
  - **Hata Düzeltme (*Edit Section*):** 5.8pt zarif öğretmen el yazısı stiliyle, metinle çakışmayan temiz düzeltme
  - **Seçenek & Şık Vurgulama:** (*Circle / underline the correct verb*)
- **📄 Adobe Acrobat Standartları:** Çözümler PDF'in çözünürlüğünü bozmaz; orijinal dosya üzerine saf siyah Helvetica vektör metin katmanı olarak basılır (Hocanın gözünde Adobe Acrobat ile doldurulmuş gibi görünür).
- **🛡️ Akıllı Kota Koruması & Otomatik Yeniden Deneme:** Google Gemini 429 hız limitlerine takılmamak için worker'lar kademeli (staggered) çalışır, geçici kota dolmalarında 2 kez otomatik yeniden dener.
- **💾 Kesintisiz Disk Önbelleği (Export Cache):** Sayfa yenilense veya tarayıcı kapansa dahi çözülen hiçbir sayfa kaybolmaz; dışa aktarırken tüm sayfalar otomatik birleştirilir.
- **📦 Toplu ZIP & Tekil PDF Dışa Aktarma:** İster tek dosya, ister birden fazla ödev kitabını tek tıkla ZIP arşivi olarak indirme.
- **✏️ Canlı Web Editörü:**
  - Çözümleri ekranda anlık düzenleme, silme ve fareyle sürükleyip taşıma
  - Klavye kısayolları (`←` / `→` ile sayfa geçişi, `Delete` ile silme)
  - Tek tıkla `+ Metin Kutusu Ekle` ile sayfanın en üstüne ad, soyad ve numara yazabilme
  - Sayfa karşılaştırma (Tek sayfa / Çift sayfa kitap görünümü)

---

## 🚀 Nasıl Başlatılır?

### Yöntem 1: Tek Tıkla Masaüstü Programı (Önerilen — En Kolayı)
1. **[Releases](https://github.com/Rel0adediso/Prepmate-PDF/releases/latest)** sayfasından **`PrepMate-PDF.exe`** dosyasını indirin.
2. Dosyaya çift tıklayın. Hepsi bu kadar! 
*(Python yüklemenize, terminal açmanıza veya paket kurmanıza gerek yoktur).*

---

### Yöntem 2: Kaynak Koddan Çalıştırma (.bat ile)
Eğer projeyi kaynak kodundan çalıştırmak veya kodları geliştirmek isterseniz:
1. Bilgisayarınızda **Python 3.10+** kurulu olmalıdır *(Kurarken "Add python.exe to PATH" seçeneğini işaretleyin)*.
2. Projeyi ZIP olarak indirin ve bir klasöre çıkartın.
3. Klasör içindeki **`kurulum.bat`** dosyasına çift tıklayın (gerekli kütüphaneleri otomatik kurar).
4. Ardından **`baslat.bat`** dosyasına çift tıklayın (tarayıcınızda otomatik açılır).

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

## 🛡️ Gizlilik ve Güvenlik (100% Yerel Çalışma)

- **Kişisel Verileriniz ve Dosyalarınız:** Yüklediğiniz PDF kitapları, ödevler ve çözümler yalnızca kendi bilgisayarınızda (localhost) işlenir; harici hiçbir sunucuya kaydedilmez.
- **API Anahtarları:** Tanımladığınız Gemini ve OpenRouter anahtarları yalnızca kendi tarayıcınızın yerel hafızasında (`localStorage`) ve yerel diskinizde tutulur. GitHub reposuna asla sızmaz.
- **Açık Kaynak Kod:** Projenin tüm kaynak kodu tamamen şeffaftır ve arka planda çalışan gizli hiçbir telemetri veya veri toplama kodu bulunmaz.
