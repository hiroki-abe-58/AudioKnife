// Tauri Commands
// Bridge between frontend and Rust backend

use crate::audio::{
    silence_padding::{add_silence_padding, get_audio_info, batch_add_silence_padding, AudioInfo},
    format_converter::{add_silence_and_convert, OutputFormat, check_ffmpeg},
};
use crate::ai_bridge::{check_backend, BackendStatus};
use std::path::Path;
use serde::{Deserialize, Serialize};

/// Result type for audio processing
#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessResult {
    pub success: bool,
    pub output_path: Option<String>,
    pub message: String,
    pub audio_info: Option<AudioInfo>,
}

/// Batch processing result
#[derive(Debug, Serialize, Deserialize)]
pub struct BatchProcessResult {
    pub total: usize,
    pub success_count: usize,
    pub failed_count: usize,
    pub results: Vec<ProcessResult>,
}

/// Get audio file information
#[tauri::command]
pub fn cmd_get_audio_info(input_path: String) -> Result<AudioInfo, String> {
    get_audio_info(Path::new(&input_path))
        .map_err(|e| e.to_string())
}

/// Add silence padding to audio file (WAV only, native Rust)
#[tauri::command]
pub fn cmd_add_silence_padding(
    input_path: String,
    output_path: String,
    pre_silence_secs: f64,
    post_silence_secs: f64,
) -> ProcessResult {
    match add_silence_padding(
        Path::new(&input_path),
        Path::new(&output_path),
        pre_silence_secs,
        post_silence_secs,
    ) {
        Ok(info) => ProcessResult {
            success: true,
            output_path: Some(output_path),
            message: format!(
                "Success: Added {}s pre-silence and {}s post-silence",
                pre_silence_secs, post_silence_secs
            ),
            audio_info: Some(info),
        },
        Err(e) => ProcessResult {
            success: false,
            output_path: None,
            message: e.to_string(),
            audio_info: None,
        },
    }
}

/// Add silence padding with format conversion (uses ffmpeg)
#[tauri::command]
pub fn cmd_add_silence_with_format(
    input_path: String,
    output_path: String,
    pre_silence_secs: f64,
    post_silence_secs: f64,
    format: String,
) -> ProcessResult {
    let output_format = match OutputFormat::from_name(&format) {
        Some(f) => f,
        None => return ProcessResult {
            success: false,
            output_path: None,
            message: format!("Unsupported format: {}", format),
            audio_info: None,
        },
    };
    
    match add_silence_and_convert(
        Path::new(&input_path),
        Path::new(&output_path),
        pre_silence_secs,
        post_silence_secs,
        output_format,
    ) {
        Ok(path) => ProcessResult {
            success: true,
            output_path: Some(path),
            message: format!(
                "Success: Added {}s pre-silence, {}s post-silence, converted to {}",
                pre_silence_secs, post_silence_secs, format
            ),
            audio_info: None,
        },
        Err(e) => ProcessResult {
            success: false,
            output_path: None,
            message: e.to_string(),
            audio_info: None,
        },
    }
}

/// Batch process multiple files with silence padding
#[tauri::command]
pub fn cmd_batch_silence_padding(
    files: Vec<(String, String)>,
    pre_silence_secs: f64,
    post_silence_secs: f64,
) -> BatchProcessResult {
    let results = batch_add_silence_padding(files.clone(), pre_silence_secs, post_silence_secs);
    
    let success_count = results.iter().filter(|r| r.is_ok()).count();
    let failed_count = results.len() - success_count;
    
    let process_results: Vec<ProcessResult> = results
        .into_iter()
        .zip(files.iter())
        .map(|(result, (_, output_path))| {
            match result {
                Ok(info) => ProcessResult {
                    success: true,
                    output_path: Some(output_path.clone()),
                    message: "Success".to_string(),
                    audio_info: Some(info),
                },
                Err(e) => ProcessResult {
                    success: false,
                    output_path: None,
                    message: e,
                    audio_info: None,
                },
            }
        })
        .collect();
    
    BatchProcessResult {
        total: process_results.len(),
        success_count,
        failed_count,
        results: process_results,
    }
}

/// Check system status (ffmpeg, Python backend, etc.)
#[tauri::command]
pub fn cmd_check_system_status() -> SystemStatus {
    SystemStatus {
        ffmpeg_available: check_ffmpeg(),
        backend_status: check_backend(),
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemStatus {
    pub ffmpeg_available: bool,
    pub backend_status: BackendStatus,
}

/// Get available output formats
#[tauri::command]
pub fn cmd_get_output_formats() -> Vec<FormatInfo> {
    vec![
        FormatInfo { name: "WAV".to_string(), extension: "wav".to_string(), description: "Lossless, large file size".to_string() },
        FormatInfo { name: "MP3 (320kbps)".to_string(), extension: "mp3".to_string(), description: "High quality compressed".to_string() },
        FormatInfo { name: "MP3 (192kbps)".to_string(), extension: "mp3".to_string(), description: "Standard quality".to_string() },
        FormatInfo { name: "MP3 (128kbps)".to_string(), extension: "mp3".to_string(), description: "Smaller file size".to_string() },
        FormatInfo { name: "AAC (256kbps)".to_string(), extension: "m4a".to_string(), description: "Apple/iOS compatible".to_string() },
        FormatInfo { name: "AAC (192kbps)".to_string(), extension: "m4a".to_string(), description: "Standard AAC".to_string() },
        FormatInfo { name: "FLAC".to_string(), extension: "flac".to_string(), description: "Lossless, compressed".to_string() },
        FormatInfo { name: "OGG (192kbps)".to_string(), extension: "ogg".to_string(), description: "Open format".to_string() },
    ]
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FormatInfo {
    pub name: String,
    pub extension: String,
    pub description: String,
}
