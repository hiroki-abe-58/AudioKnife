// AudioKnife - Apple Silicon Optimized Audio Processor
// Built with Tauri 2.0

pub mod audio;
pub mod ai_bridge;
pub mod commands;

use commands::*;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Initialize logging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .init();
    
    log::info!("AudioKnife starting...");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            cmd_get_audio_info,
            cmd_add_silence_padding,
            cmd_add_silence_with_format,
            cmd_batch_silence_padding,
            cmd_check_system_status,
            cmd_get_output_formats,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
