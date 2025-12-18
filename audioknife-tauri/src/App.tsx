import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open, save } from "@tauri-apps/plugin-dialog";
import "./App.css";

// Types
interface AudioInfo {
    sample_rate: number;
    channels: number;
    bits_per_sample: number;
    duration_secs: number;
    total_samples: number;
}

interface ProcessResult {
    success: boolean;
    output_path: string | null;
    message: string;
    audio_info: AudioInfo | null;
}

// interface BatchProcessResult {
//   total: number;
//   success_count: number;
//   failed_count: number;
//   results: ProcessResult[];
// }

interface FormatInfo {
    name: string;
    extension: string;
    description: string;
}

interface SystemStatus {
    ffmpeg_available: boolean;
    backend_status: {
        available: boolean;
        python_version: string | null;
        available_models: string[];
    };
}

// Icons as inline SVG components
const UploadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z" />
    </svg>
);

const AudioIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 3v9.28a4.39 4.39 0 0 0-1.5-.28C8.01 12 6 14.01 6 16.5S8.01 21 10.5 21c2.31 0 4.2-1.75 4.45-4H15V6h4V3h-7z" />
    </svg>
);

const SettingsIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
    </svg>
);

const ProcessIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" />
    </svg>
);

function App() {
    // State
    const [activeTab, setActiveTab] = useState<"silence" | "ai">("silence");
    const [inputFile, setInputFile] = useState<string | null>(null);
    const [audioInfo, setAudioInfo] = useState<AudioInfo | null>(null);
    const [preSilence, setPreSilence] = useState<number>(0);
    const [postSilence, setPostSilence] = useState<number>(0);
    const [outputFormat, setOutputFormat] = useState<string>("WAV");
    const [formats, setFormats] = useState<FormatInfo[]>([]);
    const [processing, setProcessing] = useState<boolean>(false);
    const [progress, setProgress] = useState<number>(0);
    const [log, setLog] = useState<string>("");
    const [result, setResult] = useState<ProcessResult | null>(null);
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

    // Load initial data
    useEffect(() => {
        loadFormats();
        checkSystemStatus();
    }, []);

    const loadFormats = async () => {
        try {
            const formatList = await invoke<FormatInfo[]>("cmd_get_output_formats");
            setFormats(formatList);
        } catch (e) {
            console.error("Failed to load formats:", e);
        }
    };

    const checkSystemStatus = async () => {
        try {
            const status = await invoke<SystemStatus>("cmd_check_system_status");
            setSystemStatus(status);
            appendLog(`System Status: FFmpeg=${status.ffmpeg_available ? "OK" : "Not Found"}, Python=${status.backend_status.python_version || "Not Found"}`);
        } catch (e) {
            console.error("Failed to check system status:", e);
        }
    };

    const appendLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setLog(prev => `${prev}[${timestamp}] ${message}\n`);
    };

    // File selection
    const selectFile = async () => {
        try {
            const selected = await open({
                multiple: false,
                filters: [{
                    name: "Audio Files",
                    extensions: ["wav", "mp3", "m4a", "flac", "ogg", "aac"]
                }]
            });

            if (selected) {
                setInputFile(selected as string);
                appendLog(`Selected: ${selected}`);

                // Get audio info
                try {
                    const info = await invoke<AudioInfo>("cmd_get_audio_info", { inputPath: selected });
                    setAudioInfo(info);
                    appendLog(`Duration: ${info.duration_secs.toFixed(2)}s, Sample Rate: ${info.sample_rate}Hz, Channels: ${info.channels}`);
                } catch (e) {
                    appendLog(`Warning: Could not read audio info (will use ffmpeg)`);
                }
            }
        } catch (e) {
            appendLog(`Error selecting file: ${e}`);
        }
    };

    // Process file
    const processFile = async () => {
        if (!inputFile) {
            appendLog("Error: No input file selected");
            return;
        }

        if (preSilence === 0 && postSilence === 0) {
            appendLog("Error: Please specify pre or post silence duration");
            return;
        }

        try {
            setProcessing(true);
            setProgress(10);
            appendLog(`Processing: ${inputFile}`);
            appendLog(`Pre-silence: ${preSilence}s, Post-silence: ${postSilence}s, Format: ${outputFormat}`);

            // Get output path
            const inputName = inputFile.split("/").pop()?.replace(/\.[^/.]+$/, "") || "output";
            const ext = formats.find(f => f.name === outputFormat)?.extension || "wav";

            const outputPath = await save({
                defaultPath: `${inputName}_padded.${ext}`,
                filters: [{
                    name: "Audio Files",
                    extensions: [ext]
                }]
            });

            if (!outputPath) {
                appendLog("Cancelled: No output path selected");
                setProcessing(false);
                return;
            }

            setProgress(30);

            // Process based on format
            let processResult: ProcessResult;

            if (outputFormat === "WAV" && inputFile.toLowerCase().endsWith(".wav")) {
                // Use native Rust processing for WAV
                appendLog("Using native Rust processing...");
                processResult = await invoke<ProcessResult>("cmd_add_silence_padding", {
                    inputPath: inputFile,
                    outputPath: outputPath,
                    preSilenceSecs: preSilence,
                    postSilenceSecs: postSilence,
                });
            } else {
                // Use ffmpeg for format conversion
                appendLog("Using ffmpeg for format conversion...");
                processResult = await invoke<ProcessResult>("cmd_add_silence_with_format", {
                    inputPath: inputFile,
                    outputPath: outputPath,
                    preSilenceSecs: preSilence,
                    postSilenceSecs: postSilence,
                    format: outputFormat,
                });
            }

            setProgress(100);
            setResult(processResult);

            if (processResult.success) {
                appendLog(`Success: ${processResult.message}`);
                appendLog(`Output: ${processResult.output_path}`);
            } else {
                appendLog(`Error: ${processResult.message}`);
            }

        } catch (e) {
            appendLog(`Error: ${e}`);
        } finally {
            setProcessing(false);
        }
    };

    // Drag and drop handling
    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // Note: Tauri handles file paths differently
            appendLog("Drag & drop detected - please use the file selector");
        }
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
    }, []);

    return (
        <div className="app-container">
            {/* Header */}
            <header className="app-header">
                <h1>AudioKnife</h1>
                <p>Apple Silicon Optimized Audio Processor</p>
            </header>

            {/* Tabs */}
            <div className="tabs-container">
                <button
                    className={`tab-button ${activeTab === "silence" ? "active" : ""}`}
                    onClick={() => setActiveTab("silence")}
                >
                    Silence Padding
                </button>
                <button
                    className={`tab-button ${activeTab === "ai" ? "active" : ""}`}
                    onClick={() => setActiveTab("ai")}
                >
                    AI Enhancement
                </button>
            </div>

            {/* Silence Padding Tab */}
            {activeTab === "silence" && (
                <div className="two-columns">
                    {/* Left Column - Input */}
                    <div>
                        <div className="card">
                            <div className="card-header">
                                <AudioIcon />
                                Input Audio
                            </div>

                            <div
                                className="drop-zone"
                                onClick={selectFile}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                            >
                                <div className="drop-zone-icon">
                                    <UploadIcon />
                                </div>
                                <div className="drop-zone-text">
                                    {inputFile ? inputFile.split("/").pop() : "Click to select audio file"}
                                </div>
                                <div className="drop-zone-hint">
                                    Supports: WAV, MP3, M4A, FLAC, OGG
                                </div>
                            </div>

                            {audioInfo && (
                                <div className="info-box info" style={{ marginTop: "12px" }}>
                                    <span>
                                        Duration: {audioInfo.duration_secs.toFixed(2)}s |
                                        Sample Rate: {audioInfo.sample_rate}Hz |
                                        Channels: {audioInfo.channels}
                                    </span>
                                </div>
                            )}
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <SettingsIcon />
                                Settings
                            </div>

                            <div className="form-group">
                                <label className="form-label">Pre-Silence (seconds)</label>
                                <div className="input-with-unit">
                                    <input
                                        type="number"
                                        className="form-input"
                                        value={preSilence}
                                        onChange={(e) => setPreSilence(parseFloat(e.target.value) || 0)}
                                        min="0"
                                        max="600"
                                        step="0.1"
                                    />
                                    <span className="input-unit">sec</span>
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Post-Silence (seconds)</label>
                                <div className="input-with-unit">
                                    <input
                                        type="number"
                                        className="form-input"
                                        value={postSilence}
                                        onChange={(e) => setPostSilence(parseFloat(e.target.value) || 0)}
                                        min="0"
                                        max="600"
                                        step="0.1"
                                    />
                                    <span className="input-unit">sec</span>
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Output Format</label>
                                <select
                                    className="form-select"
                                    value={outputFormat}
                                    onChange={(e) => setOutputFormat(e.target.value)}
                                >
                                    {formats.map((f) => (
                                        <option key={f.name} value={f.name}>
                                            {f.name} - {f.description}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <button
                                className="btn btn-primary btn-full"
                                onClick={processFile}
                                disabled={processing || !inputFile}
                            >
                                <ProcessIcon />
                                {processing ? "Processing..." : "Add Silence Padding"}
                            </button>
                        </div>
                    </div>

                    {/* Right Column - Output */}
                    <div>
                        <div className="card">
                            <div className="card-header">
                                <AudioIcon />
                                Output
                            </div>

                            {processing && (
                                <div className="progress-container">
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                                    </div>
                                    <div className="progress-text">Processing... {progress}%</div>
                                </div>
                            )}

                            {result && (
                                <div className={`info-box ${result.success ? "info" : "warning"}`}>
                                    <span>{result.message}</span>
                                </div>
                            )}

                            {result?.output_path && (
                                <div style={{ marginTop: "12px" }}>
                                    <audio controls className="audio-player" src={`file://${result.output_path}`} />
                                </div>
                            )}
                        </div>

                        <div className="card">
                            <div className="card-header">
                                Processing Log
                            </div>
                            <div className="log-output">
                                {log || "Ready..."}
                            </div>
                        </div>

                        {/* System Status */}
                        {systemStatus && (
                            <div className="card">
                                <div className="card-header">
                                    System Status
                                </div>
                                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                                    <span className={`status-badge ${systemStatus.ffmpeg_available ? "success" : "error"}`}>
                                        FFmpeg: {systemStatus.ffmpeg_available ? "Available" : "Not Found"}
                                    </span>
                                    <span className={`status-badge ${systemStatus.backend_status.available ? "success" : "warning"}`}>
                                        Python: {systemStatus.backend_status.python_version || "Not Found"}
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* AI Enhancement Tab */}
            {activeTab === "ai" && (
                <div className="card">
                    <div className="card-header">
                        AI Enhancement
                    </div>
                    <div className="info-box warning">
                        <span>
                            AI Enhancement features require the Python backend to be running.
                            This feature will be available in a future update.
                        </span>
                    </div>
                    <p style={{ marginTop: "16px", color: "var(--on-surface-variant)" }}>
                        Available AI Models:
                    </p>
                    <ul style={{ marginTop: "8px", marginLeft: "20px", color: "var(--on-surface-variant)" }}>
                        <li>Resemble Enhance (Denoise + Quality)</li>
                        <li>Demucs (BGM Removal)</li>
                        <li>Spleeter (Vocal Extraction)</li>
                        <li>MP-SENet (Speech Enhancement)</li>
                        <li>MossFormer2 (Speaker Separation)</li>
                    </ul>
                </div>
            )}
        </div>
    );
}

export default App;
