#![windows_subsystem = "windows"]

use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use serde::{Deserialize, Serialize};
use tao::{
    event::{Event, StartCause, WindowEvent},
    event_loop::{ControlFlow, EventLoopBuilder},
    window::WindowBuilder,
};
use wry::WebViewBuilder;

// ============================================================================
// DATA STRUCTURES
// ============================================================================

#[derive(Clone, Serialize, Deserialize)]
pub struct SourceDocument {
    pub name: String,
    pub path: Option<String>,
    pub pages_text: Vec<String>,
    pub is_active: bool,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct StudyNote {
    pub id: String,
    pub title: String,
    pub content: String,
    pub timestamp: String,
    pub source_ref: Option<String>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct ChapterTOC {
    pub title: String,
    pub page: usize,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct MistakeItem {
    pub id: String,
    pub question: String,
    pub student_answer: String,
    pub correct_answer: String,
    pub explanation: String,
    pub topic: String,
    pub timestamp: String,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct TopicMastery {
    pub topic_name: String,
    pub score_pct: u8,
    pub status: String,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct DailyTask {
    pub id: String,
    pub title: String,
    pub task_type: String, // "pages" | "focus" | "mistakes" | "custom"
    pub target: usize,
    pub progress: usize,
    pub is_done: bool,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct FocusSessionLog {
    pub intention: String,
    pub duration_mins: u32,
    pub pages_read: usize,
    pub timestamp: String,
    pub completed: bool,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct ExamTarget {
    pub title: String,
    pub date_str: String,
    pub target_pages: usize,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct CourseProject {
    pub id: String,
    pub title: String,
    pub icon: String,
    pub description: String,
    pub sources: Vec<SourceDocument>,
    pub active_source_idx: usize,
    pub current_page: usize,
    pub notes: Vec<StudyNote>,
    pub chapters: Vec<ChapterTOC>,
    pub mistakes: Vec<MistakeItem>,
    pub mastery_topics: Vec<TopicMastery>,
}

impl CourseProject {
    pub fn current_page_text(&self) -> String {
        if let Some(src) = self.sources.get(self.active_source_idx) {
            let idx = self.current_page.saturating_sub(1);
            src.pages_text.get(idx).cloned().unwrap_or_else(|| "Sayfa içeriği boş.".to_string())
        } else {
            "Kaynak belge bulunamadı.".to_string()
        }
    }
    pub fn total_pages(&self) -> usize {
        self.sources.get(self.active_source_idx).map(|s| s.pages_text.len()).unwrap_or(1)
    }
}

fn default_rhythm_shields() -> u8 {
    2
}

fn default_daily_tasks() -> Vec<DailyTask> {
    vec![
        DailyTask {
            id: "t_pages".to_string(),
            title: "15 Sayfa Ders Belgesi Oku".to_string(),
            task_type: "pages".to_string(),
            target: 15,
            progress: 0,
            is_done: false,
        },
        DailyTask {
            id: "t_focus".to_string(),
            title: "1 Kvieta Odak Oturumu Tamamla".to_string(),
            task_type: "focus".to_string(),
            target: 1,
            progress: 0,
            is_done: false,
        },
        DailyTask {
            id: "t_mistakes".to_string(),
            title: "Hata Defterinden 2 Yanlış Pekiştir".to_string(),
            task_type: "mistakes".to_string(),
            target: 2,
            progress: 0,
            is_done: false,
        },
    ]
}

fn generate_default_mastery_topics(chapters: &[ChapterTOC]) -> Vec<TopicMastery> {
    if !chapters.is_empty() {
        chapters.iter().take(8).enumerate().map(|(i, c)| {
            let (score, status) = match i % 3 {
                0 => (85, "good"),
                1 => (60, "review"),
                _ => (35, "critical"),
            };
            TopicMastery {
                topic_name: c.title.clone(),
                score_pct: score,
                status: status.to_string(),
            }
        }).collect()
    } else {
        vec![
            TopicMastery { topic_name: "Temel Kavramlar & Giriş".into(), score_pct: 85, status: "good".into() },
            TopicMastery { topic_name: "Formüller & Metodoloji".into(), score_pct: 65, status: "review".into() },
            TopicMastery { topic_name: "Uygulama & Problem Çözümü".into(), score_pct: 40, status: "critical".into() },
            TopicMastery { topic_name: "Analiz & Çıkarım".into(), score_pct: 70, status: "review".into() },
            TopicMastery { topic_name: "İleri Seviye Soru Tipleri".into(), score_pct: 30, status: "critical".into() },
            TopicMastery { topic_name: "Pekiştirme ve Sentez".into(), score_pct: 80, status: "good".into() },
        ]
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct AppState {
    pub projects: Vec<CourseProject>,
    pub active_project_idx: usize,
    pub gemini_api_key: String,
    pub timer_seconds: u32,
    pub timer_active: bool,
    #[serde(default = "default_daily_tasks")]
    pub daily_tasks: Vec<DailyTask>,
    #[serde(default)]
    pub streak_days: u32,
    #[serde(default = "default_rhythm_shields")]
    pub rhythm_shields: u8,
    #[serde(default)]
    pub last_study_date: String,
    #[serde(default)]
    pub focus_sessions: Vec<FocusSessionLog>,
    #[serde(default)]
    pub exam_target: Option<ExamTarget>,
}

impl AppState {
    pub fn current_project(&self) -> Option<&CourseProject> {
        self.projects.get(self.active_project_idx)
    }
    pub fn current_project_mut(&mut self) -> Option<&mut CourseProject> {
        self.projects.get_mut(self.active_project_idx)
    }
    pub fn current_page_text(&self) -> String {
        self.current_project()
            .map(|p| p.current_page_text())
            .unwrap_or_else(|| "Henüz bir ders belgesi açılmadı. 'PDF Seç' ile dosyanızı yükleyin.".to_string())
    }
}

fn get_storage_path() -> PathBuf {
    let mut p = dirs_next().unwrap_or_else(|| PathBuf::from("."));
    p.push(".prepmate_notebooks.json");
    p
}

fn dirs_next() -> Option<PathBuf> {
    std::env::var_os("USERPROFILE")
        .or_else(|| std::env::var_os("HOME"))
        .map(PathBuf::from)
}

fn get_today_string() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    let days = now / 86400;
    format!("day_{}", days)
}

fn load_state_from_disk() -> AppState {
    let path = get_storage_path();
    let today = get_today_string();
    if let Ok(bytes) = fs::read(&path) {
        if let Ok(mut st) = serde_json::from_slice::<AppState>(&bytes) {
            if st.daily_tasks.is_empty() {
                st.daily_tasks = default_daily_tasks();
            }
            for p in &mut st.projects {
                if p.mastery_topics.is_empty() {
                    p.mastery_topics = generate_default_mastery_topics(&p.chapters);
                }
            }
            if st.rhythm_shields == 0 && st.streak_days == 0 {
                st.rhythm_shields = 2;
            }
            // Check day transition for daily tasks and calculate streak & shields
            let current_day_num = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() / 86400;
            let last_day_num: u64 = st.last_study_date.strip_prefix("day_").and_then(|s| s.parse().ok()).unwrap_or(0);

            if last_day_num > 0 && current_day_num > last_day_num {
                let day_diff = current_day_num - last_day_num;
                let completed_any = st.daily_tasks.iter().any(|t| t.is_done);

                if day_diff == 1 {
                    if completed_any {
                        st.streak_days = st.streak_days.saturating_add(1);
                    } else if st.rhythm_shields > 0 {
                        st.rhythm_shields = st.rhythm_shields.saturating_sub(1);
                    } else {
                        st.streak_days = 0;
                    }
                } else {
                    // Missed more than 1 day
                    let missed_days = (day_diff - 1) as u8;
                    let total_unshielded = missed_days + if !completed_any { 1 } else { 0 };
                    if st.rhythm_shields >= total_unshielded {
                        st.rhythm_shields -= total_unshielded;
                    } else {
                        st.rhythm_shields = 0;
                        st.streak_days = 0;
                    }
                }

                for t in &mut st.daily_tasks {
                    t.progress = 0;
                    t.is_done = false;
                }
            }
            st.last_study_date = today;
            return st;
        }
    }

    AppState {
        projects: vec![],
        active_project_idx: 0,
        gemini_api_key: std::env::var("GEMINI_API_KEY").unwrap_or_default(),
        timer_seconds: 1500,
        timer_active: false,
        daily_tasks: default_daily_tasks(),
        streak_days: 1,
        rhythm_shields: 2,
        last_study_date: today,
        focus_sessions: vec![],
        exam_target: Some(ExamTarget {
            title: "B2 Hazırlık Final Sınavı".to_string(),
            date_str: "2026-11-28".to_string(),
            target_pages: 50,
        }),
    }
}

fn save_state_to_disk(st: &AppState) {
    let path = get_storage_path();
    if let Ok(json) = serde_json::to_vec_pretty(st) {
        let _ = fs::write(path, json);
    }
}

// ============================================================================
// IPC MESSAGE TYPES
// ============================================================================

#[derive(Deserialize)]
struct IpcMessage {
    action: String,
    #[serde(default)]
    text: Option<String>,
    #[serde(default)]
    key: Option<String>,
    #[serde(default)]
    page: Option<usize>,
    #[serde(default)]
    r#type: Option<String>,
    #[serde(default)]
    title: Option<String>,
    #[serde(default)]
    icon: Option<String>,
    #[serde(default)]
    description: Option<String>,
    #[serde(default)]
    project_idx: Option<usize>,
    #[serde(default)]
    question: Option<String>,
    #[serde(default)]
    student_answer: Option<String>,
    #[serde(default)]
    correct_answer: Option<String>,
    #[serde(default)]
    explanation: Option<String>,
    #[serde(default)]
    note_id: Option<String>,
    #[serde(default)]
    task_id: Option<String>,
    #[serde(default)]
    target: Option<usize>,
    #[serde(default)]
    intention: Option<String>,
    #[serde(default)]
    duration: Option<u32>,
    #[serde(default)]
    pages_read: Option<usize>,
    #[serde(default)]
    date_str: Option<String>,
}

enum UserEvent {
    ChatReply(String),
    ShowToast(String),
    ProjectLoaded(String),
    StateUpdate(String),
}

// ============================================================================
// MAIN APPLICATION ENTRY POINT (TAURI / WRY MODERN)
// ============================================================================

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let state = Arc::new(tokio::sync::Mutex::new(load_state_from_disk()));
    let rt = tokio::runtime::Runtime::new()?;

    let event_loop = EventLoopBuilder::<UserEvent>::with_user_event().build();
    let window = WindowBuilder::new()
        .with_title("PrepMate 2.0 Alpha 1 — Modern Native Studio")
        .with_inner_size(tao::dpi::LogicalSize::new(1440.0, 920.0))
        .build(&event_loop)?;

    let proxy = event_loop.create_proxy();
    let html_content = include_str!("../ui/index.html");

    let state_ipc = state.clone();
    let proxy_ipc = proxy.clone();
    let rt_handle = rt.handle().clone();

    let webview = WebViewBuilder::new()
        .with_html(html_content)
        .with_ipc_handler(move |req| {
            let body = req.body().clone();
            if let Ok(msg) = serde_json::from_str::<IpcMessage>(&body) {
                let state = state_ipc.clone();
                let proxy = proxy_ipc.clone();

                match msg.action.as_str() {
                    "get_state" => {
                        let st = state.blocking_lock();
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                    }
                    "create_course" => {
                        let title = msg.title.filter(|t| !t.trim().is_empty()).unwrap_or_else(|| "Yeni Ders".to_string());
                        let icon = msg.icon.filter(|i| !i.trim().is_empty()).unwrap_or_else(|| "📚".to_string());
                        let desc = msg.description.unwrap_or_default();

                        let mut st = state.blocking_lock();
                        let new_proj = CourseProject {
                            id: format!("proj_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                            title: title.clone(),
                            icon,
                            description: desc,
                            sources: vec![],
                            active_source_idx: 0,
                            current_page: 1,
                            notes: vec![],
                            chapters: vec![],
                            mistakes: vec![],
                            mastery_topics: generate_default_mastery_topics(&[]),
                        };
                        st.projects.push(new_proj);
                        st.active_project_idx = st.projects.len().saturating_sub(1);
                        save_state_to_disk(&st);

                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' dersi oluşturuldu! Şimdi belge ekleyebilirsiniz.", title)));
                    }
                    "add_doc_to_course" => {
                        let target_idx = msg.project_idx.or(msg.page);
                        rt_handle.spawn(async move {
                            if let Some(path) = rfd::FileDialog::new()
                                .add_filter("Ders Belgeleri (PDF, TXT, MD)", &["pdf", "txt", "md"])
                                .pick_file() 
                            {
                                let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                                let mut text_pages = Vec::new();
                                if file_name.ends_with(".pdf") {
                                    if let Ok(doc) = lopdf::Document::load(&path) {
                                        let page_count = doc.get_pages().len();
                                        for p in 1..=page_count {
                                            if let Ok(txt) = doc.extract_text(&[p as u32]) {
                                                text_pages.push(txt);
                                            } else {
                                                text_pages.push(format!("Sayfa {}", p));
                                            }
                                        }
                                    }
                                } else if let Ok(s) = fs::read_to_string(&path) {
                                    text_pages.push(s);
                                }

                                if text_pages.is_empty() {
                                    text_pages.push("Belge içeriği okundu.".to_string());
                                }

                                let total_p = text_pages.len();
                                let mut chapters = Vec::new();
                                for i in (1..=total_p).step_by(10) {
                                    chapters.push(ChapterTOC {
                                        title: format!("Bölüm (Syf {}-{})", i, (i + 9).min(total_p)),
                                        page: i,
                                    });
                                }

                                let mut st = state.lock().await;
                                let p_idx = target_idx.unwrap_or(st.active_project_idx);
                                if p_idx < st.projects.len() {
                                    st.active_project_idx = p_idx;
                                    let course_title = st.projects[p_idx].title.clone();
                                    let proj = &mut st.projects[p_idx];
                                    proj.sources.push(SourceDocument {
                                        name: file_name.clone(),
                                        path: Some(path.to_string_lossy().to_string()),
                                        pages_text: text_pages,
                                        is_active: true,
                                    });
                                    proj.active_source_idx = proj.sources.len().saturating_sub(1);
                                    proj.current_page = 1;
                                    if proj.chapters.is_empty() {
                                        proj.chapters = chapters;
                                    }
                                    if proj.mastery_topics.is_empty() {
                                        proj.mastery_topics = generate_default_mastery_topics(&proj.chapters);
                                    }
                                    let proj_json = serde_json::to_string(proj).unwrap_or_default();
                                    save_state_to_disk(&st);

                                    let state_json = serde_json::to_string(&*st).unwrap_or_default();
                                    let _ = proxy.send_event(UserEvent::StateUpdate(state_json));
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(proj_json));
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' dersine '{}' belgesi eklendi!", course_title, file_name)));
                                } else {
                                    // Fallback: create course from document
                                    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy().to_string();
                                    let new_proj = CourseProject {
                                        id: format!("proj_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                                        title: file_stem,
                                        icon: "📚".to_string(),
                                        description: format!("{} ({} Sayfa)", file_name, total_p),
                                        sources: vec![SourceDocument {
                                            name: file_name.clone(),
                                            path: Some(path.to_string_lossy().to_string()),
                                            pages_text: text_pages,
                                            is_active: true,
                                        }],
                                        active_source_idx: 0,
                                        current_page: 1,
                                        notes: vec![],
                                        chapters: chapters.clone(),
                                        mistakes: vec![],
                                        mastery_topics: generate_default_mastery_topics(&chapters),
                                    };
                                    let proj_json = serde_json::to_string(&new_proj).unwrap_or_default();
                                    st.projects.push(new_proj);
                                    st.active_project_idx = st.projects.len().saturating_sub(1);
                                    save_state_to_disk(&st);

                                    let state_json = serde_json::to_string(&*st).unwrap_or_default();
                                    let _ = proxy.send_event(UserEvent::StateUpdate(state_json));
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(proj_json));
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' yüklendi!", file_name)));
                                }
                            }
                        });
                    }
                    "open_pdf_dialog" => {
                        let target_idx = msg.project_idx.or(msg.page);
                        rt_handle.spawn(async move {
                            if let Some(path) = rfd::FileDialog::new()
                                .add_filter("Ders Belgeleri (PDF, TXT, MD)", &["pdf", "txt", "md"])
                                .pick_file() 
                            {
                                let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                                let file_stem = path.file_stem().unwrap_or_default().to_string_lossy().to_string();
                                let mut text_pages = Vec::new();
                                if file_name.ends_with(".pdf") {
                                    if let Ok(doc) = lopdf::Document::load(&path) {
                                        let page_count = doc.get_pages().len();
                                        for p in 1..=page_count {
                                            if let Ok(txt) = doc.extract_text(&[p as u32]) {
                                                text_pages.push(txt);
                                            } else {
                                                text_pages.push(format!("Sayfa {}", p));
                                            }
                                        }
                                    }
                                } else if let Ok(s) = fs::read_to_string(&path) {
                                    text_pages.push(s);
                                }

                                if text_pages.is_empty() {
                                    text_pages.push("Belge içeriği okundu.".to_string());
                                }

                                let total_p = text_pages.len();
                                let mut chapters = Vec::new();
                                for i in (1..=total_p).step_by(10) {
                                    chapters.push(ChapterTOC {
                                        title: format!("Bölüm (Syf {}-{})", i, (i + 9).min(total_p)),
                                        page: i,
                                    });
                                }

                                let mut st = state.lock().await;
                                let p_idx = target_idx.unwrap_or(st.active_project_idx);
                                if !st.projects.is_empty() && p_idx < st.projects.len() {
                                    st.active_project_idx = p_idx;
                                    let proj = &mut st.projects[p_idx];
                                    proj.sources.push(SourceDocument {
                                        name: file_name.clone(),
                                        path: Some(path.to_string_lossy().to_string()),
                                        pages_text: text_pages,
                                        is_active: true,
                                    });
                                    proj.active_source_idx = proj.sources.len().saturating_sub(1);
                                    proj.current_page = 1;
                                    if proj.chapters.is_empty() {
                                        proj.chapters = chapters.clone();
                                    }
                                    if proj.mastery_topics.is_empty() {
                                        proj.mastery_topics = generate_default_mastery_topics(&proj.chapters);
                                    }
                                    let proj_json = serde_json::to_string(proj).unwrap_or_default();
                                    save_state_to_disk(&st);

                                    let state_json = serde_json::to_string(&*st).unwrap_or_default();
                                    let _ = proxy.send_event(UserEvent::StateUpdate(state_json));
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(proj_json));
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' yüklendi!", file_name)));
                                } else {
                                    let new_proj = CourseProject {
                                        id: format!("proj_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                                        title: file_stem,
                                        icon: "📚".to_string(),
                                        description: format!("{} ({} Sayfa)", file_name, total_p),
                                        sources: vec![SourceDocument {
                                            name: file_name.clone(),
                                            path: Some(path.to_string_lossy().to_string()),
                                            pages_text: text_pages,
                                            is_active: true,
                                        }],
                                        active_source_idx: 0,
                                        current_page: 1,
                                        notes: vec![],
                                        chapters: chapters.clone(),
                                        mistakes: vec![],
                                        mastery_topics: generate_default_mastery_topics(&chapters),
                                    };

                                    let proj_json = serde_json::to_string(&new_proj).unwrap_or_default();
                                    st.projects.push(new_proj);
                                    st.active_project_idx = st.projects.len().saturating_sub(1);
                                    save_state_to_disk(&st);

                                    let state_json = serde_json::to_string(&*st).unwrap_or_default();
                                    let _ = proxy.send_event(UserEvent::StateUpdate(state_json));
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(proj_json));
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' yüklendi!", file_name)));
                                }
                            }
                        });
                    }
                    "switch_project" => {
                        if let Some(idx) = msg.page {
                            let mut st = state.blocking_lock();
                            if idx < st.projects.len() {
                                st.active_project_idx = idx;
                                save_state_to_disk(&st);
                                if let Some(p) = st.current_project() {
                                    let proj_json = serde_json::to_string(p).unwrap_or_default();
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(proj_json));
                                }
                                let json = serde_json::to_string(&*st).unwrap_or_default();
                                let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            }
                        }
                    }
                    "delete_project" => {
                        if let Some(idx) = msg.page {
                            let mut st = state.blocking_lock();
                            if idx < st.projects.len() {
                                st.projects.remove(idx);
                                if st.active_project_idx >= st.projects.len() {
                                    st.active_project_idx = st.projects.len().saturating_sub(1);
                                }
                                save_state_to_disk(&st);
                            }
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        }
                    }
                    "chat_message" => {
                        let text = msg.text.unwrap_or_default();
                        rt_handle.spawn(async move {
                            let reply = handle_chat_action(&state, &text).await;
                            let _ = proxy.send_event(UserEvent::ChatReply(reply));
                        });
                    }
                    "solve_page" => {
                        rt_handle.spawn(async move {
                            let reply = handle_solve_action(&state).await;
                            let _ = proxy.send_event(UserEvent::ChatReply(reply));
                            let _ = proxy.send_event(UserEvent::ShowToast("Sayfa çözümleri tamamlandı!".to_string()));
                        });
                    }
                    "grade_homework" => {
                        let text = msg.text.unwrap_or_default();
                        rt_handle.spawn(async move {
                            let mut st = state.lock().await;
                            let mistake = MistakeItem {
                                id: format!("mistake_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                                question: "Ödev Sorusu".to_string(),
                                student_answer: text,
                                correct_answer: "Doğru Yanıt".to_string(),
                                explanation: "Ödev kontrol sonucu oluşturuldu.".to_string(),
                                topic: "Ders Pratiği".to_string(),
                                timestamp: "Şimdi".to_string(),
                            };
                            if let Some(p) = st.current_project_mut() {
                                p.mistakes.push(mistake);
                            }
                            save_state_to_disk(&st);
                            let _ = proxy.send_event(UserEvent::ShowToast("Ödev notlandırıldı & yanlışlar Hata Defterine eklendi!".to_string()));
                        });
                    }
                    "pin_page_to_notes" => {
                        let text = msg.text.unwrap_or_else(|| {
                            let st = state.blocking_lock();
                            st.current_page_text()
                        });
                        let mut st = state.blocking_lock();
                        let mut proj_json = None;
                        let p_name = st.current_project().map(|p| p.title.clone()).unwrap_or_else(|| "Genel Not".to_string());
                        if let Some(p) = st.current_project_mut() {
                            p.notes.push(StudyNote {
                                id: format!("note_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                                title: format!("{} — Syf {}", p_name, p.current_page),
                                content: text,
                                timestamp: "Şimdi".to_string(),
                                source_ref: Some(format!("Sayfa {}", p.current_page)),
                            });
                            proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                        }
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        if let Some(pj) = proj_json {
                            let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                        }
                        let _ = proxy.send_event(UserEvent::ShowToast("Not defterine kaydedildi! 📌".to_string()));
                    }
                    "delete_note" => {
                        let n_id = msg.note_id.or(msg.text);
                        if let Some(id) = n_id {
                            let mut st = state.blocking_lock();
                            let mut proj_json = None;
                            if let Some(p) = st.current_project_mut() {
                                p.notes.retain(|n| n.id != id);
                                proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            if let Some(pj) = proj_json {
                                let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                            }
                            let _ = proxy.send_event(UserEvent::ShowToast("Not silindi.".to_string()));
                        }
                    }
                    "add_mistake" => {
                        let question = msg.question.unwrap_or_else(|| "Ders Sorusu".to_string());
                        let student_answer = msg.student_answer.unwrap_or_else(|| "Eksik / Hatalı".to_string());
                        let correct_answer = msg.correct_answer.unwrap_or_else(|| "Doğru Açıklama".to_string());
                        let explanation = msg.explanation.unwrap_or_else(|| msg.text.unwrap_or_default());

                        let mut st = state.blocking_lock();
                        let mut proj_json = None;
                        if let Some(p) = st.current_project_mut() {
                            let mistake = MistakeItem {
                                id: format!("mistake_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                                question,
                                student_answer,
                                correct_answer,
                                explanation,
                                topic: p.title.clone(),
                                timestamp: "Şimdi".to_string(),
                            };
                            p.mistakes.push(mistake);
                            proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                        }
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        if let Some(pj) = proj_json {
                            let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                        }
                        let _ = proxy.send_event(UserEvent::ShowToast("Soru Hata Defterine eklendi! 📕".to_string()));
                    }
                    "update_course" => {
                        let idx = msg.project_idx.or(msg.page);
                        let mut st = state.blocking_lock();
                        let p_idx = idx.unwrap_or(st.active_project_idx);
                        if p_idx < st.projects.len() {
                            if let Some(title) = msg.title.filter(|t| !t.trim().is_empty()) {
                                st.projects[p_idx].title = title;
                            }
                            if let Some(icon) = msg.icon.filter(|i| !i.trim().is_empty()) {
                                st.projects[p_idx].icon = icon;
                            }
                            if let Some(desc) = msg.description {
                                st.projects[p_idx].description = desc;
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            let _ = proxy.send_event(UserEvent::ShowToast("Ders bilgileri güncellendi! ✏️".to_string()));
                        }
                    }
                    "test_gemini_key" => {
                        let key = msg.key.clone();
                        rt_handle.spawn(async move {
                            let api_key = {
                                if let Some(k) = key.filter(|s| !s.trim().is_empty()) {
                                    k.trim().to_string()
                                } else {
                                    let st = state.lock().await;
                                    st.gemini_api_key.trim().to_string()
                                }
                            };
                            if api_key.is_empty() {
                                let _ = proxy.send_event(UserEvent::ShowToast("⚠️ Lütfen test etmek için önce bir API anahtarı girin.".to_string()));
                                return;
                            }
                            let client = reqwest::Client::new();
                            let url = format!("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}", api_key);
                            let body = serde_json::json!({
                                "contents": [{ "parts": [{ "text": "ping" }] }]
                            });
                            match client.post(&url).json(&body).send().await {
                                Ok(res) if res.status().is_success() => {
                                    let _ = proxy.send_event(UserEvent::ShowToast("✅ Gemini API bağlantısı başarılı! Model aktif.".to_string()));
                                }
                                Ok(res) => {
                                    let status = res.status();
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("⚠️ API Hatası (HTTP {}): Anahtar geçersiz olabilir.", status)));
                                }
                                Err(e) => {
                                    let _ = proxy.send_event(UserEvent::ShowToast(format!("⚠️ Bağlantı hatası: {}", e)));
                                }
                            }
                        });
                    }
                    "jump_page" => {
                        if let Some(p) = msg.page {
                            let mut st = state.blocking_lock();
                            let was_forward = if let Some(proj) = st.current_project() {
                                p > proj.current_page
                            } else {
                                false
                            };
                            if let Some(proj) = st.current_project_mut() {
                                proj.current_page = p;
                            }
                            if was_forward {
                                if let Some(task) = st.daily_tasks.iter_mut().find(|t| t.task_type == "pages" || t.id == "t_pages") {
                                    task.progress = (task.progress + 1).min(task.target);
                                    if task.progress >= task.target {
                                        task.is_done = true;
                                    }
                                }
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        }
                    }
                    "save_api_key" => {
                        if let Some(k) = msg.key {
                            let clean_key = k.trim().to_string();
                            let mut st = state.blocking_lock();
                            st.gemini_api_key = clean_key;
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            let _ = proxy.send_event(UserEvent::ShowToast("Gemini API anahtarı başarıyla kaydedildi!".to_string()));
                        }
                    }
                    "switch_source" => {
                        if let Some(src_idx) = msg.page {
                            let mut st = state.blocking_lock();
                            let mut proj_json = None;
                            if let Some(p) = st.current_project_mut() {
                                if src_idx < p.sources.len() {
                                    p.active_source_idx = src_idx;
                                    p.current_page = 1;
                                    let total_p = p.sources[src_idx].pages_text.len();
                                    p.chapters = (1..=total_p).step_by(10).map(|i| ChapterTOC {
                                        title: format!("Bölüm (Syf {}-{})", i, (i + 9).min(total_p)),
                                        page: i,
                                    }).collect();
                                    proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                                }
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            if let Some(pj) = proj_json {
                                let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                            }
                        }
                    }
                    "delete_source" => {
                        if let Some(s_idx) = msg.page {
                            let mut st = state.blocking_lock();
                            let mut proj_json = None;
                            if let Some(p) = st.current_project_mut() {
                                if s_idx < p.sources.len() {
                                    p.sources.remove(s_idx);
                                    p.active_source_idx = p.active_source_idx.min(p.sources.len().saturating_sub(1));
                                    p.current_page = 1;
                                    if let Some(src) = p.sources.get(p.active_source_idx) {
                                        let total_p = src.pages_text.len();
                                        p.chapters = (1..=total_p).step_by(10).map(|i| ChapterTOC {
                                            title: format!("Bölüm (Syf {}-{})", i, (i + 9).min(total_p)),
                                            page: i,
                                        }).collect();
                                    } else {
                                        p.chapters.clear();
                                    }
                                    proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                                }
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            if let Some(pj) = proj_json {
                                let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                            }
                            let _ = proxy.send_event(UserEvent::ShowToast("Belge dersten kaldırıldı.".to_string()));
                        }
                    }
                    "delete_mistake" => {
                        if let Some(m_id) = msg.text {
                            let mut st = state.blocking_lock();
                            let mut proj_json = None;
                            if let Some(p) = st.current_project_mut() {
                                p.mistakes.retain(|m| m.id != m_id);
                                proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                            }
                            if let Some(task) = st.daily_tasks.iter_mut().find(|t| t.task_type == "mistakes" || t.id == "t_mistakes") {
                                task.progress = (task.progress + 1).min(task.target);
                                if task.progress >= task.target {
                                    task.is_done = true;
                                }
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                            if let Some(pj) = proj_json {
                                let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                            }
                            let _ = proxy.send_event(UserEvent::ShowToast("Hata çözüldü olarak işaretlendi!".to_string()));
                        }
                    }
                    "save_state" => {
                        let st = state.blocking_lock();
                        save_state_to_disk(&st);
                    }
                    "add_source_dialog" => {
                        rt_handle.spawn(async move {
                            if let Some(path) = rfd::FileDialog::new()
                                .add_filter("Ders Belgeleri", &["pdf", "txt", "md"])
                                .pick_file() 
                            {
                                let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                                let mut text_pages = Vec::new();
                                if file_name.ends_with(".pdf") {
                                    if let Ok(doc) = lopdf::Document::load(&path) {
                                        for p in 1..=doc.get_pages().len() {
                                            if let Ok(txt) = doc.extract_text(&[p as u32]) {
                                                text_pages.push(txt);
                                            } else {
                                                text_pages.push(format!("Sayfa {}", p));
                                            }
                                        }
                                    }
                                } else if let Ok(s) = fs::read_to_string(&path) {
                                    text_pages.push(s);
                                }

                                if text_pages.is_empty() {
                                    text_pages.push("Belge içeriği okundu.".to_string());
                                }

                                let mut st = state.lock().await;
                                let mut proj_json = None;
                                if let Some(p) = st.current_project_mut() {
                                    p.sources.push(SourceDocument {
                                        name: file_name.clone(),
                                        path: Some(path.to_string_lossy().to_string()),
                                        pages_text: text_pages,
                                        is_active: true,
                                    });
                                    p.active_source_idx = p.sources.len().saturating_sub(1);
                                    p.current_page = 1;
                                    if p.mastery_topics.is_empty() {
                                        p.mastery_topics = generate_default_mastery_topics(&p.chapters);
                                    }
                                    proj_json = Some(serde_json::to_string(p).unwrap_or_default());
                                }
                                save_state_to_disk(&st);
                                let state_json = serde_json::to_string(&*st).unwrap_or_default();
                                let _ = proxy.send_event(UserEvent::StateUpdate(state_json));
                                if let Some(pj) = proj_json {
                                    let _ = proxy.send_event(UserEvent::ProjectLoaded(pj));
                                }
                                let _ = proxy.send_event(UserEvent::ShowToast(format!("'{}' kaynağı eklendi!", file_name)));
                            }
                        });
                    }
                    "export" => {
                        if let Some(t) = msg.r#type {
                            let st = state.blocking_lock();
                            if let Some(proj) = st.current_project() {
                                let out_dir = dirs_next().unwrap_or_else(|| PathBuf::from("."));
                                let desktop_dir = out_dir.join("Desktop");
                                let target_dir = if desktop_dir.exists() { desktop_dir } else { out_dir };

                                match t.as_str() {
                                    "save_md" => {
                                        let md = format!("# {} — Çözüm Raporu\n\n{}\n\n**Oluşturuldu:** PrepMate 2.0", proj.title, proj.current_page_text());
                                        let file_path = target_dir.join("Ders_Cozumu.md");
                                        let _ = fs::write(&file_path, md);
                                        let _ = proxy.send_event(UserEvent::ShowToast("Ders_Cozumu.md Masaüstüne kaydedildi!".to_string()));
                                    }
                                    "save_mistakes_md" => {
                                        let mut md = format!("# {} — Hata Defterim\n\n", proj.title);
                                        for (i, m) in proj.mistakes.iter().enumerate() {
                                            md.push_str(&format!("### {}. {}\n- **Senin Yanıtın:** `{}`\n- **Doğru Yanıt:** `{}`\n- **Gerekçe:** {}\n\n", i+1, m.question, m.student_answer, m.correct_answer, m.explanation));
                                        }
                                        let file_path = target_dir.join("Hata_Defterim.md");
                                        let _ = fs::write(&file_path, md);
                                        let _ = proxy.send_event(UserEvent::ShowToast("Hata_Defterim.md Masaüstüne kaydedildi!".to_string()));
                                    }
                                    "backup_json" => {
                                        if let Ok(json) = serde_json::to_string_pretty(&*st) {
                                            let file_path = target_dir.join("PrepMate_Yedek.json");
                                            let _ = fs::write(&file_path, json);
                                            let _ = proxy.send_event(UserEvent::ShowToast("PrepMate_Yedek.json Masaüstüne yedeklendi!".to_string()));
                                        }
                                    }
                                    _ => {}
                                }
                            }
                        }
                    }
                    "open_external_url" => {
                        if let Some(url) = msg.text {
                            let _ = std::process::Command::new("rundll32")
                                .args(["url.dll,FileProtocolHandler", &url])
                                .spawn();
                        }
                    }
                    "start_focus_session" => {
                        let intention = msg.intention.unwrap_or_else(|| "Ders Çalışma & Odaklanma".to_string());
                        let duration = msg.duration.unwrap_or(25);
                        let _ = proxy.send_event(UserEvent::ShowToast(format!("🎯 Kvieta Odak Başladı: '{}' ({} dk)", intention, duration)));
                    }
                    "finish_focus_session" => {
                        let intention = msg.intention.unwrap_or_else(|| "Odaklanma Seansı".to_string());
                        let duration = msg.duration.unwrap_or(25);
                        let pages = msg.pages_read.unwrap_or(0);
                        let mut st = state.blocking_lock();
                        st.focus_sessions.push(FocusSessionLog {
                            intention: intention.clone(),
                            duration_mins: duration,
                            pages_read: pages,
                            timestamp: "Bugün".to_string(),
                            completed: true,
                        });
                        if let Some(task) = st.daily_tasks.iter_mut().find(|t| t.task_type == "focus" || t.id == "t_focus") {
                            task.progress = (task.progress + 1).min(task.target);
                            if task.progress >= task.target {
                                task.is_done = true;
                            }
                        }
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        let _ = proxy.send_event(UserEvent::ShowToast(format!("🎉 Harika! {} dk odak oturumu tamamlandı.", duration)));
                    }
                    "toggle_daily_task" => {
                        if let Some(t_id) = msg.task_id.or(msg.text) {
                            let mut st = state.blocking_lock();
                            if let Some(task) = st.daily_tasks.iter_mut().find(|t| t.id == t_id) {
                                task.is_done = !task.is_done;
                                if task.is_done {
                                    task.progress = task.target;
                                } else {
                                    task.progress = 0;
                                }
                            }
                            save_state_to_disk(&st);
                            let json = serde_json::to_string(&*st).unwrap_or_default();
                            let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        }
                    }
                    "add_daily_task" => {
                        let title = msg.title.unwrap_or_else(|| "Yeni Günlük Hedef".to_string());
                        let target = msg.target.unwrap_or(1);
                        let task_type = msg.r#type.unwrap_or_else(|| "custom".to_string());
                        let mut st = state.blocking_lock();
                        st.daily_tasks.push(DailyTask {
                            id: format!("task_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis()),
                            title,
                            task_type,
                            target,
                            progress: 0,
                            is_done: false,
                        });
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        let _ = proxy.send_event(UserEvent::ShowToast("Yeni günlük hedef eklendi! 📋".to_string()));
                    }
                    "advance_page_progress" => {
                        let mut st = state.blocking_lock();
                        if let Some(task) = st.daily_tasks.iter_mut().find(|t| t.task_type == "pages" || t.id == "t_pages") {
                            task.progress = (task.progress + 1).min(task.target);
                            if task.progress >= task.target {
                                task.is_done = true;
                            }
                        }
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                    }
                    "save_exam_target" => {
                        let title = msg.title.unwrap_or_else(|| "Final Sınavı".to_string());
                        let date_str = msg.date_str.unwrap_or_else(|| "2026-06-20".to_string());
                        let target_pages = msg.target.unwrap_or(50);
                        let mut st = state.blocking_lock();
                        st.exam_target = Some(ExamTarget {
                            title,
                            date_str,
                            target_pages,
                        });
                        save_state_to_disk(&st);
                        let json = serde_json::to_string(&*st).unwrap_or_default();
                        let _ = proxy.send_event(UserEvent::StateUpdate(json));
                        let _ = proxy.send_event(UserEvent::ShowToast("Sınav hedefi kaydedildi! 🎯".to_string()));
                    }
                    "reinforce_topic" => {
                        let topic_name = msg.title.unwrap_or_else(|| "Bu Konu".to_string());
                        let st_clone = state.clone();
                        let pr_clone = proxy.clone();
                        rt_handle.spawn(async move {
                            let prompt = format!("Öğrenci '{}' konusunda zorlanıyor. Bu konuyu pekiştirmek için:\n1. 2 cümlelik pratik özet kural,\n2. 1 adet sınav tarzı soru,\n3. Çözüm tekniği ve dikkat edilmesi gereken tuzakları açıkla.", topic_name);
                            let reply = handle_chat_action(&st_clone, &prompt).await;
                            let _ = pr_clone.send_event(UserEvent::ChatReply(reply));
                            let _ = pr_clone.send_event(UserEvent::ShowToast(format!("'{}' için pekiştirme rehberi Co-Worker paneline aktarıldı!", topic_name)));
                        });
                    }
                    _ => {}
                }
            }
        })
        .build(&window)?;

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        match event {
            Event::NewEvents(StartCause::Init) => {},
            Event::UserEvent(user_event) => {
                match user_event {
                    UserEvent::ChatReply(reply) => {
                        let script = format!("window.onRustChatReply({})", serde_json::to_string(&reply).unwrap_or_default());
                        let _ = webview.evaluate_script(&script);
                    }
                    UserEvent::ShowToast(msg) => {
                        let script = format!("showToast({})", serde_json::to_string(&msg).unwrap_or_default());
                        let _ = webview.evaluate_script(&script);
                    }
                    UserEvent::ProjectLoaded(json) => {
                        let script = format!("window.onProjectLoaded({})", json);
                        let _ = webview.evaluate_script(&script);
                    }
                    UserEvent::StateUpdate(json) => {
                        let script = format!("window.onStateUpdate({})", json);
                        let _ = webview.evaluate_script(&script);
                    }
                }
            }
            Event::WindowEvent { event: WindowEvent::CloseRequested, .. } => {
                *control_flow = ControlFlow::Exit;
            }
            _ => (),
        }
    });
}

// ============================================================================
// ASYNC SERVICE LOGIC (GEMINI API STREAMING & SOLVER)
// ============================================================================

async fn handle_chat_action(state: &Arc<tokio::sync::Mutex<AppState>>, prompt: &str) -> String {
    let (key_raw, context) = {
        let st = state.lock().await;
        (st.gemini_api_key.clone(), st.current_page_text())
    };

    let key = key_raw.trim();
    if key.is_empty() {
        return format!("🤖 **Bilgi:** Gemini API anahtarınız henüz girilmedi.\nSağ üstteki **⚙️ Ayarlar** simgesine tıklayarak ücretsiz Google AI Studio API anahtarınızı kaydedebilirsiniz.\n\n*Çalışma Modu İpucu:* Takıldığınız soruların kuralını veya çözüm adımlarını sormaya devam edebilirsiniz.");
    }

    let client = reqwest::Client::new();
    let url = format!("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}", key);
    let sys_prompt = format!("Sen PrepMate Co-Worker Study Partner'sın. Açık ders belgesi içeriği:\n{}\n\nÖğrencinin sorusu:\n{}", context, prompt);

    let body = serde_json::json!({
        "contents": [{ "parts": [{ "text": sys_prompt }] }]
    });

    if let Ok(res) = client.post(&url).json(&body).send().await {
        if let Ok(json) = res.json::<serde_json::Value>().await {
            if let Some(text) = json["candidates"][0]["content"]["parts"][0]["text"].as_str() {
                return text.to_string();
            }
        }
    }

    "⚠️ Gemini API yanıtı alınamadı, lütfen internet bağlantınızı ve API anahtarınızı kontrol edin.".to_string()
}

async fn handle_solve_action(state: &Arc<tokio::sync::Mutex<AppState>>) -> String {
    let prompt = "Bu sayfadaki tüm soruları ve alıştırmaları sırasıyla çöz, doğru cevapları ve kısa Türkçe açıklamalarını düzenli bir liste halinde ver.";
    handle_chat_action(state, prompt).await
}
