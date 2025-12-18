// Format Converter Module
// Handles audio format conversion using ffmpeg subprocess

use std::path::Path;
use std::process::Command;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FormatError {
    #[error("FFmpeg not found")]
    FfmpegNotFound,
    #[error("Conversion failed: {0}")]
    ConversionFailed(String),
    #[error("Unsupported format: {0}")]
    UnsupportedFormat(String),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// Supported output formats
#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize)]
pub enum OutputFormat {
    Wav,
    Mp3High,    // 320kbps
    Mp3Medium,  // 192kbps
    Mp3Low,     // 128kbps
    AacHigh,    // 256kbps
    AacMedium,  // 192kbps
    Flac,
    Ogg,        // 192kbps
}

impl OutputFormat {
    /// Get file extension for the format
    pub fn extension(&self) -> &'static str {
        match self {
            OutputFormat::Wav => "wav",
            OutputFormat::Mp3High | OutputFormat::Mp3Medium | OutputFormat::Mp3Low => "mp3",
            OutputFormat::AacHigh | OutputFormat::AacMedium => "m4a",
            OutputFormat::Flac => "flac",
            OutputFormat::Ogg => "ogg",
        }
    }
    
    /// Get ffmpeg codec arguments for the format
    pub fn ffmpeg_args(&self) -> Vec<&'static str> {
        match self {
            OutputFormat::Wav => vec!["-c:a", "pcm_s16le"],
            OutputFormat::Mp3High => vec!["-c:a", "libmp3lame", "-b:a", "320k"],
            OutputFormat::Mp3Medium => vec!["-c:a", "libmp3lame", "-b:a", "192k"],
            OutputFormat::Mp3Low => vec!["-c:a", "libmp3lame", "-b:a", "128k"],
            OutputFormat::AacHigh => vec!["-c:a", "aac", "-b:a", "256k"],
            OutputFormat::AacMedium => vec!["-c:a", "aac", "-b:a", "192k"],
            OutputFormat::Flac => vec!["-c:a", "flac"],
            OutputFormat::Ogg => vec!["-c:a", "libvorbis", "-b:a", "192k"],
        }
    }
    
    /// Get format from string name
    pub fn from_name(name: &str) -> Option<Self> {
        match name.to_lowercase().as_str() {
            "wav" => Some(OutputFormat::Wav),
            "mp3_high" | "mp3 (320kbps)" => Some(OutputFormat::Mp3High),
            "mp3_medium" | "mp3 (192kbps)" => Some(OutputFormat::Mp3Medium),
            "mp3_low" | "mp3 (128kbps)" => Some(OutputFormat::Mp3Low),
            "aac_high" | "aac (256kbps)" => Some(OutputFormat::AacHigh),
            "aac_medium" | "aac (192kbps)" => Some(OutputFormat::AacMedium),
            "flac" => Some(OutputFormat::Flac),
            "ogg" | "ogg (192kbps)" => Some(OutputFormat::Ogg),
            _ => None,
        }
    }
}

/// Check if ffmpeg is available
pub fn check_ffmpeg() -> bool {
    Command::new("ffmpeg")
        .arg("-version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

/// Convert audio file to specified format using ffmpeg
/// 
/// # Arguments
/// * `input_path` - Path to input audio file
/// * `output_path` - Path to output audio file (extension will be added)
/// * `format` - Target output format
/// 
/// # Returns
/// * `Result<String, FormatError>` - Output file path on success
pub fn convert_format(
    input_path: &Path,
    output_path: &Path,
    format: OutputFormat,
) -> Result<String, FormatError> {
    if !check_ffmpeg() {
        return Err(FormatError::FfmpegNotFound);
    }
    
    // Build output path with correct extension
    let output_with_ext = output_path
        .with_extension(format.extension());
    
    // Build ffmpeg command
    let mut cmd = Command::new("ffmpeg");
    cmd.arg("-y")  // Overwrite output
       .arg("-i").arg(input_path)
       .args(format.ffmpeg_args())
       .arg(&output_with_ext);
    
    let output = cmd.output()?;
    
    if output.status.success() {
        Ok(output_with_ext.to_string_lossy().to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(FormatError::ConversionFailed(stderr.to_string()))
    }
}

/// Add silence padding and convert to specified format
/// 
/// This combines silence padding with format conversion in one operation
/// using ffmpeg's filter_complex for efficiency
pub fn add_silence_and_convert(
    input_path: &Path,
    output_path: &Path,
    pre_silence_secs: f64,
    post_silence_secs: f64,
    format: OutputFormat,
) -> Result<String, FormatError> {
    if !check_ffmpeg() {
        return Err(FormatError::FfmpegNotFound);
    }
    
    // Get audio info using ffprobe
    let probe_output = Command::new("ffprobe")
        .args(["-v", "quiet", "-print_format", "json", "-show_streams"])
        .arg(input_path)
        .output()?;
    
    // Parse sample rate and channels (default to stereo 44.1kHz)
    let (sample_rate, channel_layout) = parse_audio_info(&probe_output.stdout)
        .unwrap_or((44100, "stereo".to_string()));
    
    // Build output path with correct extension
    let output_with_ext = output_path
        .with_extension(format.extension());
    
    // Build ffmpeg command with silence padding
    let mut cmd = Command::new("ffmpeg");
    cmd.arg("-y");
    
    if pre_silence_secs > 0.0 && post_silence_secs > 0.0 {
        // Add silence before and after
        cmd.args(["-f", "lavfi", "-t", &pre_silence_secs.to_string()])
           .arg("-i").arg(format!("anullsrc=r={}:cl={}", sample_rate, channel_layout))
           .arg("-i").arg(input_path)
           .args(["-f", "lavfi", "-t", &post_silence_secs.to_string()])
           .arg("-i").arg(format!("anullsrc=r={}:cl={}", sample_rate, channel_layout))
           .args(["-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1"]);
    } else if pre_silence_secs > 0.0 {
        // Add silence before only
        cmd.args(["-f", "lavfi", "-t", &pre_silence_secs.to_string()])
           .arg("-i").arg(format!("anullsrc=r={}:cl={}", sample_rate, channel_layout))
           .arg("-i").arg(input_path)
           .args(["-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1"]);
    } else if post_silence_secs > 0.0 {
        // Add silence after only
        cmd.arg("-i").arg(input_path)
           .args(["-f", "lavfi", "-t", &post_silence_secs.to_string()])
           .arg("-i").arg(format!("anullsrc=r={}:cl={}", sample_rate, channel_layout))
           .args(["-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1"]);
    } else {
        // No silence, just convert
        cmd.arg("-i").arg(input_path);
    }
    
    // Add format-specific codec arguments
    cmd.args(format.ffmpeg_args())
       .arg(&output_with_ext);
    
    let output = cmd.output()?;
    
    if output.status.success() {
        Ok(output_with_ext.to_string_lossy().to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(FormatError::ConversionFailed(stderr.to_string()))
    }
}

/// Parse audio info from ffprobe JSON output
fn parse_audio_info(json_bytes: &[u8]) -> Option<(u32, String)> {
    let json_str = std::str::from_utf8(json_bytes).ok()?;
    let json: serde_json::Value = serde_json::from_str(json_str).ok()?;
    
    let streams = json.get("streams")?.as_array()?;
    
    for stream in streams {
        if stream.get("codec_type")?.as_str()? == "audio" {
            let sample_rate = stream.get("sample_rate")?
                .as_str()?
                .parse::<u32>()
                .ok()?;
            
            let channels = stream.get("channels")?
                .as_u64()
                .unwrap_or(2) as u32;
            
            let channel_layout = if channels == 1 { "mono" } else { "stereo" };
            
            return Some((sample_rate, channel_layout.to_string()));
        }
    }
    
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_format_extension() {
        assert_eq!(OutputFormat::Wav.extension(), "wav");
        assert_eq!(OutputFormat::Mp3High.extension(), "mp3");
        assert_eq!(OutputFormat::AacHigh.extension(), "m4a");
        assert_eq!(OutputFormat::Flac.extension(), "flac");
    }
    
    #[test]
    fn test_format_from_name() {
        assert!(matches!(OutputFormat::from_name("wav"), Some(OutputFormat::Wav)));
        assert!(matches!(OutputFormat::from_name("MP3_HIGH"), Some(OutputFormat::Mp3High)));
        assert!(OutputFormat::from_name("invalid").is_none());
    }
}
