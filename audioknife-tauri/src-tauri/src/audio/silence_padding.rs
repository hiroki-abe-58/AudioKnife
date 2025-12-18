// Silence Padding Module
// High-performance silence padding using native Rust

use hound::{WavReader, WavWriter, WavSpec, SampleFormat};
use std::path::Path;
use thiserror::Error;
use rayon::prelude::*;

#[derive(Error, Debug)]
pub enum SilencePaddingError {
    #[error("Failed to read audio file: {0}")]
    ReadError(String),
    #[error("Failed to write audio file: {0}")]
    WriteError(String),
    #[error("Unsupported audio format: {0}")]
    UnsupportedFormat(String),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// Audio file information
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct AudioInfo {
    pub sample_rate: u32,
    pub channels: u16,
    pub bits_per_sample: u16,
    pub duration_secs: f64,
    pub total_samples: u64,
}

/// Get audio file information
pub fn get_audio_info(input_path: &Path) -> Result<AudioInfo, SilencePaddingError> {
    let reader = WavReader::open(input_path)
        .map_err(|e| SilencePaddingError::ReadError(e.to_string()))?;
    
    let spec = reader.spec();
    let total_samples = reader.len() as u64;
    let duration_secs = total_samples as f64 / spec.sample_rate as f64 / spec.channels as f64;
    
    Ok(AudioInfo {
        sample_rate: spec.sample_rate,
        channels: spec.channels,
        bits_per_sample: spec.bits_per_sample,
        duration_secs,
        total_samples,
    })
}

/// Generate silence samples for the given duration
fn generate_silence_samples(spec: &WavSpec, duration_secs: f64) -> Vec<i32> {
    let num_samples = (spec.sample_rate as f64 * duration_secs * spec.channels as f64) as usize;
    vec![0i32; num_samples]
}

/// Add silence padding to an audio file (WAV format)
/// 
/// # Arguments
/// * `input_path` - Path to input audio file
/// * `output_path` - Path to output audio file
/// * `pre_silence_secs` - Seconds of silence to add before audio
/// * `post_silence_secs` - Seconds of silence to add after audio
/// 
/// # Returns
/// * `Result<AudioInfo, SilencePaddingError>` - Info about the output file
pub fn add_silence_padding(
    input_path: &Path,
    output_path: &Path,
    pre_silence_secs: f64,
    post_silence_secs: f64,
) -> Result<AudioInfo, SilencePaddingError> {
    // Open input file
    let mut reader = WavReader::open(input_path)
        .map_err(|e| SilencePaddingError::ReadError(e.to_string()))?;
    
    let spec = reader.spec();
    
    // Validate format
    if spec.sample_format != SampleFormat::Int {
        return Err(SilencePaddingError::UnsupportedFormat(
            "Only integer sample format is supported".to_string()
        ));
    }
    
    // Read all samples from input
    let input_samples: Vec<i32> = reader.samples::<i32>()
        .map(|s| s.unwrap_or(0))
        .collect();
    
    // Generate silence
    let pre_silence = generate_silence_samples(&spec, pre_silence_secs);
    let post_silence = generate_silence_samples(&spec, post_silence_secs);
    
    // Combine: pre_silence + input + post_silence
    let total_samples = pre_silence.len() + input_samples.len() + post_silence.len();
    let mut output_samples = Vec::with_capacity(total_samples);
    output_samples.extend(pre_silence);
    output_samples.extend(input_samples);
    output_samples.extend(post_silence);
    
    // Write output file
    let mut writer = WavWriter::create(output_path, spec)
        .map_err(|e| SilencePaddingError::WriteError(e.to_string()))?;
    
    for sample in output_samples.iter() {
        match spec.bits_per_sample {
            8 => writer.write_sample(*sample as i8)
                .map_err(|e| SilencePaddingError::WriteError(e.to_string()))?,
            16 => writer.write_sample(*sample as i16)
                .map_err(|e| SilencePaddingError::WriteError(e.to_string()))?,
            24 | 32 => writer.write_sample(*sample)
                .map_err(|e| SilencePaddingError::WriteError(e.to_string()))?,
            _ => return Err(SilencePaddingError::UnsupportedFormat(
                format!("Unsupported bits per sample: {}", spec.bits_per_sample)
            )),
        }
    }
    
    writer.finalize()
        .map_err(|e| SilencePaddingError::WriteError(e.to_string()))?;
    
    // Return output info
    let duration_secs = output_samples.len() as f64 / spec.sample_rate as f64 / spec.channels as f64;
    
    Ok(AudioInfo {
        sample_rate: spec.sample_rate,
        channels: spec.channels,
        bits_per_sample: spec.bits_per_sample,
        duration_secs,
        total_samples: output_samples.len() as u64,
    })
}

/// Batch process multiple files with silence padding (parallel processing using Rayon)
/// 
/// # Arguments
/// * `files` - Vector of (input_path, output_path) tuples
/// * `pre_silence_secs` - Seconds of silence to add before audio
/// * `post_silence_secs` - Seconds of silence to add after audio
/// 
/// # Returns
/// * `Vec<Result<AudioInfo, String>>` - Results for each file
pub fn batch_add_silence_padding(
    files: Vec<(String, String)>,
    pre_silence_secs: f64,
    post_silence_secs: f64,
) -> Vec<Result<AudioInfo, String>> {
    files.par_iter()
        .map(|(input, output)| {
            add_silence_padding(
                Path::new(input),
                Path::new(output),
                pre_silence_secs,
                post_silence_secs,
            ).map_err(|e| e.to_string())
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    
    #[test]
    fn test_generate_silence() {
        let spec = WavSpec {
            channels: 2,
            sample_rate: 44100,
            bits_per_sample: 16,
            sample_format: SampleFormat::Int,
        };
        
        let silence = generate_silence_samples(&spec, 1.0);
        assert_eq!(silence.len(), 44100 * 2); // 1 second * 2 channels
        assert!(silence.iter().all(|&s| s == 0));
    }
}
