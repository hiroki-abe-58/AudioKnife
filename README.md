# AudioCleaner

<div align="center">

**AI-Powered Audio Enhancement Tool**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

[English](#english) | [日本語](#japanese)

</div>

---

<a name="english"></a>
## English

### Overview

**AudioCleaner** is a powerful audio enhancement tool that combines state-of-the-art AI models to clean and enhance audio files. Available as both CLI and Web GUI interface.

### Features

- **Noise Reduction**: Powered by Facebook Research's [Denoiser](https://github.com/facebookresearch/denoiser)
  - Real-time speech enhancement in the waveform domain
  - Removes background noise, static, and unwanted sounds
  - CPU-optimized for stable performance on M1/M2/M3 Macs

- **Audio Enhancement**: Powered by [VoiceFixer](https://github.com/haoheliu/voicefixer)
  - Restores audio quality from degraded recordings
  - Enhances clarity and fidelity
  - Multiple processing modes for different noise levels

- **SE/Noise Separation**: Powered by [Resemble Enhance](https://github.com/resemble-ai/resemble-enhance)
  - Removes sound effects (SE), applause, environmental noise
  - Extracts clean voice from noisy audio
  - Optional high-quality audio enhancement with neural network

- **BGM Removal**: Powered by [Demucs](https://github.com/facebookresearch/demucs)
  - High-quality vocal extraction from music
  - Removes background music from podcasts/videos

- **Multiple Interfaces**
  - **CLI**: Command-line interface with drag-and-drop support
  - **GUI**: Web-based interface powered by Gradio
  - Real-time processing feedback
  - Built-in audio preview (macOS)

### Processing Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **0 - Standard** | Balanced processing (Recommended) | General audio cleanup |
| **1 - High Noise** | Aggressive noise reduction | Recordings with significant background noise |
| **2 - Severely Degraded** | Maximum restoration | Very poor quality recordings |
| **D - Denoiser Only** | Noise reduction without enhancement | Quick basic cleanup |
| **M - BGM Removal** | Demucs vocal extraction | Music/BGM removal from podcasts |
| **R - Resemble Denoise** | SE/Noise removal (Fast) | Remove sound effects, applause, background noise |
| **E - Resemble Enhance** | Denoise + Quality boost | High-quality enhancement with noise removal |

### Project Structure

```
AudioCleaner/
├── app_gui.py                 # Gradio Web GUI application
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
│
├── launchers/                 # Launch scripts
│   ├── audio_cleaner.command        # Basic CLI
│   ├── audio_cleaner_pro.command    # Pro CLI (all features)
│   └── audio_cleaner_gui.command    # Web GUI
│
├── scripts/                   # Processing modules
│   ├── run_resemble_enhance.py      # Resemble Enhance
│   ├── run_clearSound.py            # Denoiser
│   └── run_sepformer.py             # SepFormer
│
├── denoiser/                  # Facebook Denoiser module
├── docs/                      # Documentation
└── example/                   # Example files
```

### Prerequisites

- macOS (tested on macOS 12+, Apple Silicon recommended)
- Python 3.10 or higher
- 8GB+ RAM recommended
- Audio files in common formats (WAV, MP3, FLAC, etc.)

### Installation

#### 1. Clone the Repository

```bash
git clone git@github.com:hiroki-abe-58/AudioKnife.git
cd AudioKnife
```

#### 2. Run the Installation Script

```bash
chmod +x install.sh
./install.sh
```

This will automatically:
- Create Python virtual environment
- Install required dependencies
- Download pre-trained AI models

#### 3. (Optional) Install Additional Components

For BGM removal (Demucs):
```bash
python3.10 -m venv ~/demucs_venv310
source ~/demucs_venv310/bin/activate
pip install demucs
```

### Usage

#### GUI Mode (Recommended)

Launch the web-based GUI:
```bash
./launchers/audio_cleaner_gui.command
```
Then open http://127.0.0.1:7860 in your browser.

#### CLI Mode

Basic mode:
```bash
./launchers/audio_cleaner.command
```

Pro mode (includes BGM removal, Resemble Enhance):
```bash
./launchers/audio_cleaner_pro.command
```

1. Drag and drop your audio file into the terminal window
2. Select processing mode (press Enter for default)
3. Wait for processing to complete
4. Find your cleaned audio file in the same directory

#### Output Format

Output files are saved as:
```
YYYY-MM-DD_HH-MM-SS__original_filename_cleaned.wav
```

### Performance

Typical processing time on M1/M2 MacBook Pro:
- 1 minute audio: ~30-60 seconds
- 5 minute audio: ~3-5 minutes

Processing time scales linearly with audio duration.

### Troubleshooting

#### "Module not found" Error

```bash
cd AudioCleaner
source venv/bin/activate
pip install -r requirements.txt
```

#### Processing is Slow

- CPU processing takes time - this is normal
- Close other applications to free up resources
- Use Resemble Denoise (R) mode for faster processing

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

This project builds upon the excellent work of:

- **Facebook Research Denoiser**: [github.com/facebookresearch/denoiser](https://github.com/facebookresearch/denoiser)
  - License: CC-BY-NC 4.0

- **VoiceFixer**: [github.com/haoheliu/voicefixer](https://github.com/haoheliu/voicefixer)
  - License: MIT

- **Resemble Enhance**: [github.com/resemble-ai/resemble-enhance](https://github.com/resemble-ai/resemble-enhance)
  - License: MIT

- **Demucs**: [github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)
  - License: MIT

---

<a name="japanese"></a>
## 日本語

### 概要

**AudioCleaner**は、最先端のAIモデルを組み合わせた強力な音声クリーンアップツールです。CLIとWeb GUIの両方のインターフェースを提供します。

### 機能

- **ノイズ除去**: Facebook Researchの[Denoiser](https://github.com/facebookresearch/denoiser)を使用
  - 波形領域でのリアルタイム音声強調
  - 背景ノイズ、ホワイトノイズ、不要な音を除去
  - M1/M2/M3 Mac上で安定動作するCPU最適化

- **音質向上**: [VoiceFixer](https://github.com/haoheliu/voicefixer)を使用
  - 劣化した録音から音質を復元
  - 明瞭度と忠実度を向上
  - ノイズレベルに応じた複数の処理モード

- **SE・ノイズ分離**: [Resemble Enhance](https://github.com/resemble-ai/resemble-enhance)を使用
  - 効果音（SE）、拍手、環境音などを除去
  - ノイズのある音声からクリアな音声を抽出
  - ニューラルネットワークによる高品質な音声強化

- **BGM除去**: [Demucs](https://github.com/facebookresearch/demucs)を使用
  - 音楽から高品質なボーカル抽出
  - ポッドキャスト/動画からBGMを除去

- **複数のインターフェース**
  - **CLI**: ドラッグ&ドロップ対応のコマンドライン
  - **GUI**: Gradioを使用したWebインターフェース
  - リアルタイム処理フィードバック

### 処理モード

| モード | 説明 | 最適な用途 |
|--------|------|------------|
| **0 - 標準** | バランスの取れた処理（推奨） | 一般的な音声クリーンアップ |
| **1 - ノイズ多** | 積極的なノイズ除去 | 背景ノイズが大きい録音 |
| **2 - 激劣化** | 最大限の復元 | 品質の低い録音 |
| **D - Denoiserのみ** | 基本的なノイズ除去 | 簡単なクリーンアップ |
| **M - BGM除去** | Demucsボーカル抽出 | BGM除去 |
| **R - Resemble Denoise** | SE・ノイズ除去（高速） | 効果音、拍手、環境音の除去 |
| **E - Resemble Enhance** | ノイズ除去+音質向上 | 高品質な処理 |

### プロジェクト構造

```
AudioCleaner/
├── app_gui.py                 # Gradio Web GUI
├── install.sh                 # インストールスクリプト
├── requirements.txt           # 依存関係
├── README.md
│
├── launchers/                 # 起動スクリプト
│   ├── audio_cleaner.command        # 基本CLI
│   ├── audio_cleaner_pro.command    # Pro CLI
│   └── audio_cleaner_gui.command    # Web GUI
│
├── scripts/                   # 処理モジュール
├── denoiser/                  # Denoiserモジュール
└── docs/                      # ドキュメント
```

### 動作環境

- macOS（macOS 12以降、Apple Silicon推奨）
- Python 3.10以上
- 推奨RAM：8GB以上

### インストール

#### 1. リポジトリのクローン

```bash
git clone git@github.com:hiroki-abe-58/AudioKnife.git
cd AudioKnife
```

#### 2. インストールスクリプトの実行

```bash
chmod +x install.sh
./install.sh
```

#### 3.（オプション）追加コンポーネントのインストール

BGM除去（Demucs）を使用する場合：
```bash
python3.10 -m venv ~/demucs_venv310
source ~/demucs_venv310/bin/activate
pip install demucs
```

### 使い方

#### GUIモード（推奨）

```bash
./launchers/audio_cleaner_gui.command
```
ブラウザで http://127.0.0.1:7860 を開きます。

#### CLIモード

基本モード：
```bash
./launchers/audio_cleaner.command
```

Proモード（BGM除去、Resemble Enhance対応）：
```bash
./launchers/audio_cleaner_pro.command
```

1. 音声ファイルをターミナルにドラッグ&ドロップ
2. 処理モードを選択（Enterでデフォルト）
3. 処理完了を待つ
4. 同じディレクトリにクリーンアップされたファイルが保存される

#### 出力形式

```
YYYY-MM-DD_HH-MM-SS__元のファイル名_cleaned.wav
```

### パフォーマンス

M1/M2 MacBook Proでの処理時間：
- 1分の音声：約30〜60秒
- 5分の音声：約3〜5分

### ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)ファイルを参照。

### 謝辞

以下のプロジェクトを使用しています：

- **Facebook Research Denoiser**: [github.com/facebookresearch/denoiser](https://github.com/facebookresearch/denoiser)
- **VoiceFixer**: [github.com/haoheliu/voicefixer](https://github.com/haoheliu/voicefixer)
- **Resemble Enhance**: [github.com/resemble-ai/resemble-enhance](https://github.com/resemble-ai/resemble-enhance)
- **Demucs**: [github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)

---

**Made with care for the audio community**
