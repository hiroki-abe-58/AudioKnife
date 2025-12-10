# AudioCleaner Launcher

## 🚀 ダブルクリックで起動

`run-audioCleaner.command` をダブルクリックするだけで、AudioCleanerが起動します。

## 機能

### 自動インストールチェック

起動時に以下を自動チェック：

1. **Python 3** - インストール状態
2. **仮想環境** - venvの存在
3. **基本依存関係** - PyTorch等
4. **Denoiser** - スクリプト存在
5. **メインスクリプト** - 実行ファイル

### 自動セットアップ

必要なファイルが不足している場合：

1. 自動的に検出
2. インストール確認
3. ユーザーの承認後に自動インストール
4. 完了後に自動起動

### バージョン選択

両バージョンがインストールされている場合：

- **標準版** - 高速なノイズ除去・音質向上
- **PRO版** - SE除去機能付き

## 使用方法

### Finderから起動

1. Finderで `AudioCleaner` フォルダを開く
2. `run-audioCleaner.command` をダブルクリック
3. 画面の指示に従う

### ターミナルから起動

```bash
cd /Users/abehiroki/HotDoc/AudioCleaner
./run-audioCleaner.command
```

## 初回起動時の流れ

### 1. インストールチェック

```
╔═══════════════════════════════════════╗
║    AudioCleaner Launcher             ║
╚═══════════════════════════════════════╝

インストール状態を確認中...

  [1/5] Python 3... ✓ 3.10.5
  [2/5] 仮想環境... ✗ 未作成
  [3/5] 基本依存関係... ✗ 未インストール
  [4/5] Denoiser... ✓ 存在
  [5/5] メインスクリプト... ✓ 存在
```

### 2. セットアップ確認

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  セットアップが必要です
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AudioCleanerを使用するには、初回セットアップが必要です。
以下がインストールされます：

  • Python仮想環境
  • PyTorch & TorchAudio
  • 音声処理ライブラリ
  • AIモデル（約3-4GB）

処理時間：約5-10分
インターネット接続が必要です。

今すぐセットアップを実行しますか？ [Y/n]:
```

### 3. 自動インストール

`Y` を選択すると：

```
━━━ セットアップを開始します ━━━

[1/5] Checking Python version...
✓ Found Python 3.10.5

[2/5] Setting up base environment...
✓ Created virtual environment

[3/5] Installing base dependencies...
✓ Base dependencies installed

...
```

### 4. バージョン選択（インストール完了後）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AudioCleaner バージョン選択
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. AudioCleaner 標準版
   • ノイズ除去（Denoiser）
   • 音質向上（VoiceFixer）
   • 高速処理

2. AudioCleaner PRO
   • SE（効果音）除去機能
   • AudioSep統合
   • SepFormer-DNS統合
   • 最高品質（処理時間長め）

Q. 終了

選択 [1/2/Q]:
```

### 5. 起動

選択したバージョンが起動します。

## 2回目以降の起動

インストール済みの場合は即座にバージョン選択画面へ：

```
✓ インストール済み - すぐに起動できます

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AudioCleaner バージョン選択
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

選択 [1/2/Q]:
```

## PRO版の自動セットアップ

PRO版を選択時、依存関係が不足している場合：

```
PRO版の依存関係が不足しています。
PRO版をインストールしますか？

[Y/n]:
```

`Y` で自動的に `install_pro.sh` を実行します。

## トラブルシューティング

### ダブルクリックで起動しない

**原因**: 実行権限がない

**解決**:
```bash
chmod +x /Users/abehiroki/HotDoc/AudioCleaner/run-audioCleaner.command
```

### "Python not found"

**原因**: Python 3がインストールされていない

**解決**:
```bash
# Homebrewでインストール
brew install python3

# または公式サイトからダウンロード
# https://www.python.org/downloads/
```

### セットアップが途中で止まる

**原因**: インターネット接続またはディスク容量

**確認**:
1. インターネット接続を確認
2. ディスク空き容量を確認（5GB以上推奨）
3. 他のアプリケーションを閉じる

**再試行**:
```bash
./install.sh
```

### "audio_cleaner.command が見つかりません"

**原因**: ファイルが不足

**確認**:
```bash
ls -la audio_cleaner.command
ls -la audio_cleaner_pro.command
```

少なくとも1つのバージョンが必要です。

## 高度な使用方法

### 標準版を直接起動

```bash
./audio_cleaner.command
```

### PRO版を直接起動

```bash
./audio_cleaner_pro.command
```

### 強制再インストール

```bash
rm -rf venv
./run-audioCleaner.command
```

### PRO版依存関係のみ追加

```bash
./install_pro.sh
```

## ファイル構造

```
AudioCleaner/
├── run-audioCleaner.command  ⭐ ダブルクリックで起動
├── audio_cleaner.command      # 標準版本体
├── audio_cleaner_pro.command  # PRO版本体
├── install.sh                 # 標準版インストーラー
├── install_pro.sh             # PRO版インストーラー
└── ...
```

## 特徴

### ✅ 自動インストールチェック
起動時に必要なファイルを自動確認

### ✅ ワンクリックセットアップ
不足があれば自動的にインストール

### ✅ バージョン選択
標準版とPRO版を簡単に切り替え

### ✅ エラーハンドリング
問題があればわかりやすく表示

### ✅ ユーザーフレンドリー
技術的な知識不要で使用可能

## システム要件

### 必須
- macOS 12.0以降
- Python 3.8以降
- 5GB以上のディスク空き容量
- インターネット接続（初回のみ）

### 推奨
- M1/M2 Mac
- 8GB以上のRAM
- SSD

## FAQ

### Q: セットアップにどれくらい時間がかかる？

**A**: 約5-10分です。インターネット速度に依存します。

### Q: オフラインで使える？

**A**: 初回セットアップ後はオフラインで使用できます。

### Q: 標準版とPRO版の違いは？

**A**: 
- **標準版**: 高速、基本的なノイズ除去
- **PRO版**: SE除去、最高品質、処理時間長め

### Q: アンインストール方法は？

**A**: 
```bash
rm -rf AudioCleaner/
```

フォルダごと削除するだけです。

### Q: 更新方法は？

**A**: 
1. 新しいバージョンをダウンロード
2. 古いフォルダを削除
3. 新しいフォルダを配置
4. `run-audioCleaner.command` をダブルクリック

## サポート

問題が発生した場合：

1. [README.md](README.md) を確認
2. [README_PRO.md](README_PRO.md) を確認（PRO版）
3. GitHub Issuesで報告

---

**シンプル、高速、自動 - AudioCleaner Launcher**

