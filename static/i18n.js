// PrepMate PDF - Internationalization (i18n) Module
// Multi-language support: English (en) and Turkish (tr)

(function () {
  const translations = {
    en: {
      // General & Header
      app_title: "PrepMate PDF — AI Workbook & Homework Solver",
      api_key_btn: "AI Key",
      download_hw_btn: "Download Homework",
      download_hw_title: "Fill and export homework pages only in Acrobat vector standard",
      download_full_btn: "Book",
      download_full_title: "Download full workbook with completed exercises",
      download_zip_btn: "ZIP",
      download_zip_title: "Download all solved pages as a ZIP archive",
      lang_btn_title: "Dili Türkçe yap / Switch Language",

      // Upload Section
      hero_badge: "✨ 6x Parallel Solving • Auto-Formatting",
      hero_title: "Upload Workbook PDF",
      hero_desc: "Select your assigned course book or worksheet; pages are filled in seconds.",
      drop_title: "Drag & drop PDF here or click to browse",
      drop_subtitle: "Workbook, course book, or homework sheet (.pdf)",
      demo_btn_text: "🎯 Try Sample English Homework",
      demo_btn_badge: "1-Click Start",
      demo_btn_loading: "⏳ Preparing Sample PDF...",
      total_pages_label: "Total: {count} Pages",
      change_file_btn: "Change",
      page_range_label: "Which Pages to Solve? (Homework Page Range)",
      page_range_example: "e.g. 15-20 or 14, 15, 18",
      page_range_placeholder: "e.g. 15-20",
      page_range_hint: "Tip: Entering 15-20 will solve pages 15, 16, 17, 18, 19, and 20 only.",

      // Modes
      mode_fast_title: "Fast Mode",
      mode_fast_badge: "Parallel Solving",
      mode_fast_desc: "Direct concise answers, maximum speed with parallel workers.",
      mode_detailed_title: "Detailed Mode",
      mode_detailed_badge: "Explanations",
      mode_detailed_desc: "Includes answer rationales, grammar rules, and vocabulary definitions.",
      mode_check_title: "Check Mode",
      mode_check_badge: "Verification & Score",
      mode_check_desc: "Inspects existing answers on the page, verifies accuracy, and scores.",
      btn_fast: "⚡ Fast",
      btn_detailed: "💡 Detailed",
      btn_check: "🔍 Check",

      // CEFR & Student Touch
      cefr_title: "Target Language Level",
      cefr_desc: "Vocabulary/grammar suited for grade",
      cefr_a1: "A1 (Beginner)",
      cefr_a2: "A2 (Elementary)",
      cefr_b1: "B1 (Standard)",
      cefr_b2: "B2 (Upper-Int.)",
      cefr_c1: "C1 (Advanced)",
      human_touch_title: "Natural Student Touch",
      human_touch_badge: "Avoid AI Suspicion",
      human_touch_desc: "~95% target grade, realistic human margin",
      start_solve_btn: "⚡ Fetch Pages & Solve Automatically",

      // Editor Toolbar
      prev_page_title: "Previous Page",
      page_prefix: "Page:",
      next_page_title: "Next Page",
      two_page_btn: "📖 2 Pages",
      single_page_btn: "📄 Single",
      add_text_btn: "+ Text",
      add_text_title: "Add text box to page",
      font_size_title: "Font Size",
      resolve_btn_title: "Re-solve this page with AI",
      undo_title: "Undo (Ctrl + Z)",
      redo_title: "Redo (Ctrl + Y)",
      parchment_title: "Parchment Mode: Warm antique paper filter",
      cheat_sheet_btn: "Answers",
      cheat_sheet_title: "View numbered answer key for this page",
      copy_image_btn: "Copy",
      copy_image_title: "Copy page with answers to clipboard as high-res image (Ctrl+V to paste)",
      copy_image_loading: "Copying...",
      add_pages_btn: "Add",
      add_pages_title: "Add new pages to current list",
      progress_btn: "Progress",
      progress_btn_title: "Homework Progress",
      exit_btn: "✕ Exit",
      exit_title: "Go Back to Upload",

      // Canvas
      loading_status_text: "AI is solving questions and placing answers on the page...",
      loading_subtext: "Please wait a few seconds",
      left_page_alt: "Left Page",
      right_page_alt: "Right Page",

      // Sidebar
      sidebar_title: "Homework Progress",
      sidebar_close_title: "Close Panel",
      sidebar_status_checking: "Checking pages...",
      sidebar_status_all_done: "All pages solved! Ready to export.",
      sidebar_status_solving: "Solving in progress...",
      solve_remaining_btn: "⚡ Solve Remaining",
      solve_remaining_title: "Solve pending pages",
      completed_count: "{n} completed",
      pages_count: "{n} pages",
      sidebar_add_pages: "➕ Add New Pages",
      page_card_page: "Page {n}",
      page_card_solved: "{n} answers placed",
      page_card_reading: "Instruction / Reading page",
      page_card_solving: "Solving now...",
      page_card_pending: "Waiting in queue...",
      page_card_error: "Error occurred",
      btn_retry: "Retry",

      // Modals - Cheat Sheet
      cheat_sheet_modal_title: "Quick Answer Key",
      cheat_sheet_modal_subtitle: "Page Answer List",
      cheat_sheet_copy_all: "📋 Copy All Answers",
      cheat_sheet_empty: "No answers found on this page.",
      modal_close: "Close",

      // Modals - API Key
      api_modal_title: "Google Gemini API Key",
      api_modal_desc: "Paste your free API key from Google AI Studio. You can enter multiple keys separated by commas for multi-key round-robin.",
      api_key_placeholder: "AIzaSy... or comma-separated multiple keys",
      api_clear: "Clear",
      api_save: "Save",

      // Modals - Add Pages
      add_pages_modal_title: "Add New Pages",
      current_pages_label: "Current Pages:",
      add_pages_range_label: "Page Range to Add:",
      add_pages_placeholder: "e.g. 21-25 or 30",
      modal_cancel: "Cancel",
      modal_add_confirm: "Add and Solve",

      // Modals - Preview Notice
      preview_notice_title: "Important Note About Preview",
      preview_notice_subtitle: "Adobe Acrobat Vector Output Standard",
      preview_notice_body1: "The in-browser canvas preview may vary slightly depending on your display scaling.",
      preview_notice_body2: "✨ <b>Don't worry:</b> When you click <i>\"Download\"</i>, the generated PDF is rendered in <b>pixel-crisp, pure-black vector Acrobat text</b> directly over the original workbook!",
      dont_show_again: "Don't show this notice again",
      dismiss_notice_btn: "Got it, Continue",

      // Modals - Summary Report
      summary_report_title: "Bulk Solving Report",
      report_total_pages_label: "Total Pages Reviewed:",
      report_solved_pages_label: "✅ Homework Pages Solved:",
      report_guide_pages_label: "ℹ️ Reading / Explanatory Pages:",
      report_answers_label: "✨ Total Answers & Highlights Placed:",
      report_download_hw: "Download Homework Only",
      report_download_full: "Download Full Book",

      // Toasts & Alerts
      toast_undo_empty: "ℹ️ No actions to undo.",
      toast_undo_success: "↩️ <b>Undone</b> (Page {page})",
      toast_redo_empty: "ℹ️ No actions to redo.",
      toast_redo_success: "↪️ <b>Redone</b> (Page {page})",
      toast_key_saved_single: "API Key saved successfully.",
      toast_key_saved_multi: "{count} API Keys saved! Automatic failover enabled.",
      toast_key_cleared: "API Key cleared.",
      toast_mode_check: "Check Mode active: Your answers will be verified.",
      toast_mode_detailed: "Detailed Mode active: Explanations and rationales will be included.",
      toast_mode_fast: "Fast Mode active: Maximum speed and parallel solving.",
      toast_cefr_set: "🎯 Target Language Level: <b>{level}</b>",
      toast_human_touch_on: "🎭 <b>Natural Student Mode:</b> Realistic margin of error simulated with ~95% target grade.",
      toast_human_touch_off: "🤖 <b>Flawless Mode:</b> Questions will be answered with 100% precision.",
      toast_demo_ready: 'Sample homework loaded! Click "Fetch Pages" to try.',
      toast_pdf_only: "Please upload a valid PDF file only.",
      toast_upload_success: "PDF uploaded successfully ({pages} pages)",
      toast_enter_api_key: "Please enter your Gemini API key first.",
      toast_invalid_range: "Please enter a valid page range (1-{max})",
      toast_copy_image_success: "📸 Page image copied to clipboard! (Paste with Ctrl+V)",
      toast_copy_image_error: "Could not copy image to clipboard.",
      toast_copy_answers_success: "📋 All answers copied to clipboard!",
      toast_export_preparing: "Preparing PDF...",
      toast_export_success: "PDF downloaded successfully!",
      toast_add_text_mode: "Click anywhere on the page to place a new text box.",
      toast_delete_box_hint: "Box deleted (Use Ctrl+Z to undo)",
      toast_box_copied: "Answer copied to clipboard"
    },

    tr: {
      // General & Header
      app_title: "PrepMate PDF — AI Workbook & Ödev Çözücü",
      api_key_btn: "AI Anahtarı",
      download_hw_btn: "Ödevi İndir",
      download_hw_title: "Yalnızca ödev sayfalarını doldurup Acrobat vektörel formatında indir",
      download_full_btn: "Kitap",
      download_full_title: "Tüm çalışma kitabını indir",
      download_zip_btn: "ZIP",
      download_zip_title: "Tüm çözülen ödevleri tek bir ZIP arşivi olarak indir",
      lang_btn_title: "Switch to English / Dili Değiştir",

      // Upload Section
      hero_badge: "✨ 6x Paralel Çözüm • Otomatik Format",
      hero_title: "Workbook PDF'ini Yükle",
      hero_desc: "Hocanın verdiği ders kitabını veya ödev föyünü seç, sayfaları saniyeler içinde doldursun.",
      drop_title: "PDF dosyasını buraya sürükleyin veya tıklayın",
      drop_subtitle: "Workbook, ders kitabı veya ödev föyü (.pdf)",
      demo_btn_text: "🎯 Örnek İngilizce Ödev ile Hemen Dene",
      demo_btn_badge: "Tek Tıkla Başla",
      demo_btn_loading: "⏳ Örnek PDF Hazırlanıyor...",
      total_pages_label: "Toplam: {count} Sayfa",
      change_file_btn: "Değiştir",
      page_range_label: "Hangi Sayfalar Çözülecek? (Ödev Sayfa Aralığı)",
      page_range_example: "Örn: 15-20 veya 14, 15, 18",
      page_range_placeholder: "Örn: 15-20",
      page_range_hint: "İpucu: 15-20 yazarsanız sadece 15, 16, 17, 18, 19 ve 20. sayfalar çözülür.",

      // Modes
      mode_fast_title: "Hızlı Mod",
      mode_fast_badge: "Paralel Çözüm",
      mode_fast_desc: "Doğrudan net cevaplar, maksimum hız ve paralel worker'lar.",
      mode_detailed_title: "Detaylı Mod",
      mode_detailed_badge: "Açıklamalı Çözüm",
      mode_detailed_desc: "Cevapların gerekçeleri, dilbilgisi kuralları ve kelime anlamları eklenir.",
      mode_check_title: "Kontrol Modu",
      mode_check_badge: "Doğrulama & Puan",
      mode_check_desc: "Sayfadaki mevcut cevapları inceler, doğruluğunu kontrol eder ve puanlar.",
      btn_fast: "⚡ Hızlı",
      btn_detailed: "💡 Detaylı",
      btn_check: "🔍 Kontrol",

      // CEFR & Student Touch
      cefr_title: "Hedef Dil Seviyesi",
      cefr_desc: "Sınıfa uygun kelime/gramer",
      cefr_a1: "A1 (Başlangıç)",
      cefr_a2: "A2 (Temel)",
      cefr_b1: "B1 (Standart)",
      cefr_b2: "B2 (İleri Düzey)",
      cefr_c1: "C1 (Akademik)",
      human_touch_title: "Doğal Öğrenci Hissi",
      human_touch_badge: "Hoca Şüphelenmesin",
      human_touch_desc: "~%95 puan hedefi, masum esneme",
      start_solve_btn: "⚡ Sayfaları Getir ve Otomatik Çöz",

      // Editor Toolbar
      prev_page_title: "Önceki Sayfa",
      page_prefix: "Sayfa:",
      next_page_title: "Sonraki Sayfa",
      two_page_btn: "📖 2 Sayfa",
      single_page_btn: "📄 Tek",
      add_text_btn: "+ Metin",
      add_text_title: "Sayfaya metin kutusu ekle",
      font_size_title: "Yazı Boyutu",
      resolve_btn_title: "Bu sayfayı yapay zekayla tekrar çöz",
      undo_title: "Geri Al (Ctrl + Z)",
      redo_title: "İleri Al (Ctrl + Y)",
      parchment_title: "Göz Koruma: Sayfalara sıcak parşömen filtresi uygula",
      cheat_sheet_btn: "Cevaplar",
      cheat_sheet_title: "Bu sayfadaki tüm soruların numaralı cevap dökümünü aç",
      copy_image_btn: "Kopyala",
      copy_image_title: "Aktif sayfayı çözümleriyle birlikte resim olarak panoya kopyala (Ctrl+V ile yapıştır)",
      copy_image_loading: "Kopyalanıyor...",
      add_pages_btn: "Ekle",
      add_pages_title: "Mevcut listeye yeni sayfalar ekle",
      progress_btn: "İlerleme",
      progress_btn_title: "Ödev İlerlemesi",
      exit_btn: "✕ Çık",
      exit_title: "Geri Dön",

      // Canvas
      loading_status_text: "Yapay zeka soruları çözüyor ve boşluklara yerleştiriyor...",
      loading_subtext: "Lütfen birkaç saniye bekleyin",
      left_page_alt: "Sol Sayfa",
      right_page_alt: "Sağ Sayfa",

      // Sidebar
      sidebar_title: "Ödev İlerlemesi",
      sidebar_close_title: "Paneli Kapat",
      sidebar_status_checking: "Sayfalar kontrol ediliyor...",
      sidebar_status_all_done: "Tüm sayfalar çözüldü! İndirmeye hazır.",
      sidebar_status_solving: "Sayfalar çözülüyor...",
      solve_remaining_btn: "⚡ Kalanı Çöz",
      solve_remaining_title: "Henüz çözülmemiş sayfaları çöz",
      completed_count: "{n} tamamlandı",
      pages_count: "{n} sayfa",
      sidebar_add_pages: "➕ Yeni Sayfa Ekle",
      page_card_page: "Sayfa {n}",
      page_card_solved: "{n} cevap yerleştirildi",
      page_card_reading: "Konu Anlatımı / Bilgi Sayfası",
      page_card_solving: "Çözülüyor...",
      page_card_pending: "Sırada bekliyor...",
      page_card_error: "Hata oluştu",
      btn_retry: "Tekrar Dene",

      // Modals - Cheat Sheet
      cheat_sheet_modal_title: "Hızlı Cevap Kağıdı",
      cheat_sheet_modal_subtitle: "Sayfa Cevap Listesi",
      cheat_sheet_copy_all: "📋 Tüm Cevapları Kopyala",
      cheat_sheet_empty: "Bu sayfada henüz cevap bulunamadı.",
      modal_close: "Kapat",

      // Modals - API Key
      api_modal_title: "Google Gemini API Anahtarı",
      api_modal_desc: "Google AI Studio'dan aldığınız tamamen ücretsiz anahtarı yapıştırın. Birden fazla anahtar girerek hızı katlayabilirsiniz.",
      api_key_placeholder: "AIzaSy... veya virgülle birden fazla anahtar",
      api_clear: "Temizle",
      api_save: "Kaydet",

      // Modals - Add Pages
      add_pages_modal_title: "Yeni Sayfalar Ekle",
      current_pages_label: "Mevcut Sayfalar:",
      add_pages_range_label: "Eklenecek Sayfa Aralığı:",
      add_pages_placeholder: "Örn: 21-25 veya 30",
      modal_cancel: "Vazgeç",
      modal_add_confirm: "Ekle ve Çöz",

      // Modals - Preview Notice
      preview_notice_title: "Önizleme Hakkında Önemli Not",
      preview_notice_subtitle: "Adobe Acrobat Vektörel Çıktı Standardı",
      preview_notice_body1: "Tarayıcı ekranındaki önizleme, ekran çözünürlüğünüze göre hafif farklı görünebilir.",
      preview_notice_body2: "✨ <b>Merak etmeyin:</b> <i>\"İndir\"</i> dediğinizde oluşturulan PDF çıktısı orijinal kitap üzerine <b>milimetrik hassasiyetle ve saf siyah Acrobat vektör metni</b> olarak kusursuz basılır!",
      dont_show_again: "Bu uyarıyı bir daha gösterme",
      dismiss_notice_btn: "Anladım, Devam Et",

      // Modals - Summary Report
      summary_report_title: "Toplu Çözüm Raporu",
      report_total_pages_label: "İncelenen Toplam Sayfa:",
      report_solved_pages_label: "✅ Çözülen Ödev Sayfası:",
      report_guide_pages_label: "ℹ️ Konu Anlatımı / Bilgi Sayfası:",
      report_answers_label: "✨ Yerleştirilen Toplam Cevap & Vurgu:",
      report_download_hw: "Sadece Ödevi İndir",
      report_download_full: "Tüm Kitabı İndir",

      // Toasts & Alerts
      toast_undo_empty: "ℹ️ Geri alınacak işlem yok.",
      toast_undo_success: "↩️ <b>Geri Alındı</b> (Sayfa {page})",
      toast_redo_empty: "ℹ️ İleri alınacak işlem yok.",
      toast_redo_success: "↪️ <b>İleri Alındı</b> (Sayfa {page})",
      toast_key_saved_single: "API Anahtarı başarıyla kaydedildi.",
      toast_key_saved_multi: "{count} API Anahtarı kaydedildi! Kota doldukça otomatik geçiş yapılacak.",
      toast_key_cleared: "API Anahtarı temizlendi.",
      toast_mode_check: "Ödev Kontrol Modu aktif: Cevaplarınız doğrulanacak.",
      toast_mode_detailed: "Detaylı Mod aktif: Cevap gerekçeleri ve açıklamalar eklenecek.",
      toast_mode_fast: "Hızlı Mod aktif: Maksimum hız ve paralel çözüm.",
      toast_cefr_set: "🎯 Hedef Dil Seviyesi: <b>{level}</b>",
      toast_human_touch_on: "🎭 <b>Doğal Öğrenci Modu:</b> ~%95 puan hedefiyle gerçekçi insan hata payı simüle edilecek.",
      toast_human_touch_off: "🤖 <b>Kusursuz Mod:</b> Sorular %100 doğrulukla çözülecek.",
      toast_demo_ready: 'Örnek ödev yüklendi! "Sayfaları Getir" butonuna basarak deneyebilirsin.',
      toast_pdf_only: "Lütfen sadece PDF dosyası yükleyin.",
      toast_upload_success: "PDF başarıyla yüklendi ({pages} sayfa)",
      toast_enter_api_key: "Lütfen önce Gemini API anahtarınızı girin.",
      toast_invalid_range: "Lütfen geçerli bir sayfa aralığı girin (1-{max})",
      toast_copy_image_success: "📸 Sayfa resmi panoya kopyalandı! (Ctrl+V ile yapıştırabilirsiniz)",
      toast_copy_image_error: "Resim panoya kopyalanamadı.",
      toast_copy_answers_success: "📋 Tüm cevaplar panoya kopyalandı!",
      toast_export_preparing: "PDF Hazırlanıyor...",
      toast_export_success: "PDF başarıyla indirildi!",
      toast_add_text_mode: "Sayfada istediğiniz yere tıklayarak metin kutusu ekleyin.",
      toast_delete_box_hint: "Kutu silindi (Geri almak için Ctrl+Z)",
      toast_box_copied: "Cevap panoya kopyalandı"
    }
  };

  // Determine initial language: localStorage > navigator.language > 'en'
  let currentLang = localStorage.getItem('prepmate_lang');
  if (!currentLang) {
    const navLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
    currentLang = navLang.startsWith('tr') ? 'tr' : 'en';
  }

  function t(key, params = {}) {
    const langDict = translations[currentLang] || translations.en;
    let str = langDict[key] || translations.en[key] || key;
    if (params && typeof params === 'object') {
      Object.keys(params).forEach(k => {
        str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), params[k]);
      });
    }
    return str;
  }

  function applyLanguage(lang) {
    if (lang !== 'en' && lang !== 'tr') lang = 'en';
    currentLang = lang;
    localStorage.setItem('prepmate_lang', lang);
    document.documentElement.lang = lang;

    // Update elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = t(key);
      if (text) el.innerHTML = text;
    });

    // Update titles with data-i18n-title
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      const text = t(key);
      if (text) el.title = text;
    });

    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const text = t(key);
      if (text) el.placeholder = text;
    });

    // Update Language toggle button display
    const langToggleBtn = document.getElementById('langToggleBtn');
    const langToggleText = document.getElementById('langToggleText');
    if (langToggleText) {
      langToggleText.textContent = currentLang.toUpperCase();
    }
    if (langToggleBtn) {
      langToggleBtn.title = t('lang_btn_title');
    }

    // Dispatch event so app.js can re-render dynamic content (sidebar, cheat sheet, etc.)
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: currentLang } }));
  }

  function toggleLanguage() {
    const nextLang = currentLang === 'en' ? 'tr' : 'en';
    applyLanguage(nextLang);
  }

  // Export globally
  window.i18n = {
    t,
    setLanguage: applyLanguage,
    toggleLanguage,
    getLanguage: () => currentLang,
    translations
  };

  // Run initial translation when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => applyLanguage(currentLang));
  } else {
    applyLanguage(currentLang);
  }
})();
