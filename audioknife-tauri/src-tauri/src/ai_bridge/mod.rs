// AI Bridge Module
// Handles communication with Python AI backend via HTTP

use std::process::{Command, Stdio, Child};
use std::io::{BufRead, BufReader};
use thiserror::Error;
use serde::{Deserialize, Serialize};

const BACKEND_URL: &str = "http://127.0.0.1:8765";

#[derive(Error, Debug)]
pub enum AiBridgeError {
    #[error("Python backend not available")]
    BackendNotAvailable,
    #[error("Processing failed: {0}")]
    ProcessingFailed(String),
    #[error("Connection error: {0}")]
    ConnectionError(String),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// AI Processing modes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProcessingMode {
    ResembleDenoise,
    ResembleEnhance,
    Demucs,
    Spleeter2Stems,
    Spleeter4Stems,
    Spleeter5Stems,
    MpSenet,
    MossFormer2,
    VoiceFixer,
    DenoiserOnly,
}

impl ProcessingMode {
    pub fn to_string(&self) -> &'static str {
        match self {
            ProcessingMode::ResembleDenoise => "resemble_denoise",
            ProcessingMode::ResembleEnhance => "resemble_enhance",
            ProcessingMode::Demucs => "demucs",
            ProcessingMode::Spleeter2Stems => "spleeter_2stems",
            ProcessingMode::Spleeter4Stems => "spleeter_4stems",
            ProcessingMode::Spleeter5Stems => "spleeter_5stems",
            ProcessingMode::MpSenet => "mp_senet",
            ProcessingMode::MossFormer2 => "mossformer2",
            ProcessingMode::VoiceFixer => "voicefixer",
            ProcessingMode::DenoiserOnly => "denoiser_only",
        }
    }
}

/// AI Backend status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendStatus {
    pub available: bool,
    pub python_version: Option<String>,
    pub available_models: Vec<String>,
}

/// Check if Python backend is available
pub fn check_backend() -> BackendStatus {
    let python_check = Command::new("python3")
        .args(["--version"])
        .output();
    
    match python_check {
        Ok(output) if output.status.success() => {
            let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
            BackendStatus {
                available: true,
                python_version: Some(version),
                available_models: vec![
                    "resemble_denoise".to_string(),
                    "resemble_enhance".to_string(),
                    "demucs".to_string(),
                    "spleeter".to_string(),
                    "mp_senet".to_string(),
                    "mossformer2".to_string(),
                ],
            }
        }
        _ => BackendStatus {
            available: false,
            python_version: None,
            available_models: vec![],
        },
    }
}

/// Process audio file using Python AI backend
/// 
/// # Arguments
/// * `input_path` - Path to input audio file
/// * `output_path` - Path to output audio file
/// * `mode` - Processing mode to use
/// * `python_script_path` - Path to Python processing script
/// 
/// # Returns
/// * `Result<String, AiBridgeError>` - Output file path on success
pub fn process_with_ai(
    input_path: &str,
    output_path: &str,
    mode: ProcessingMode,
    python_script_path: &str,
) -> Result<String, AiBridgeError> {
    let mut cmd = Command::new("python3");
    cmd.arg(python_script_path)
       .arg(input_path)
       .arg("-o").arg(output_path)
       .arg("-m").arg(mode.to_string())
       .stdout(Stdio::piped())
       .stderr(Stdio::piped());
    
    let mut child = cmd.spawn()?;
    
    // Read output in real-time
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            if let Ok(line) = line {
                log::info!("AI Backend: {}", line);
            }
        }
    }
    
    let status = child.wait()?;
    
    if status.success() {
        Ok(output_path.to_string())
    } else {
        Err(AiBridgeError::ProcessingFailed(
            format!("Process exited with code: {:?}", status.code())
        ))
    }
}

/// Progress callback type for AI processing
pub type ProgressCallback = Box<dyn Fn(f32, &str) + Send + Sync>;

/// Process audio with progress reporting
pub async fn process_with_ai_async(
    input_path: String,
    output_path: String,
    mode: ProcessingMode,
    python_script_path: String,
    on_progress: Option<ProgressCallback>,
) -> Result<String, AiBridgeError> {
    tokio::task::spawn_blocking(move || {
        if let Some(callback) = &on_progress {
            callback(0.0, "Starting AI processing...");
        }
        
        let result = process_with_ai(
            &input_path,
            &output_path,
            mode,
            &python_script_path,
        );
        
        if let Some(callback) = &on_progress {
            callback(1.0, "Processing complete");
        }
        
        result
    })
    .await
    .map_err(|e| AiBridgeError::ProcessingFailed(e.to_string()))?
}
