# AudioCleaner PRO - クイックスタート

## 5分で始める

### ステップ 1: インストール（初回のみ）

```bash
cd ~/HotDoc/AudioCleaner
./install_pro.sh
```

待つだけ（20-30分）。自動的に：
- PyTorch/TorchAudioインストール
- AudioSep（GitHub版）インストール
- SpeechBrainインストール
- モデルダウンロード（~2.5GB）

### ステップ 2: 実行

```bash
./audio_cleaner_pro.command
```

### ステップ 3: ファイルを選択

音声ファイルをドラッグ&ドロップ

### ステップ 4: モードを選択

**初めての方**: `S` と入力してEnter

### ステップ 5: 待つ

処理中...（5分の音声なら10-15分）

### ステップ 6: 完了！

元のファイルと同じフォルダに `YYYY-MM-DD_HH-MM-SS__元ファイル名_cleaned.wav` が生成されます。

---

## モード早見表

| モード | 用途 | 処理時間 | 品質 |
|-------|------|----------|------|
| **S** | SE除去（推奨） | 遅い | 最高 |
| **A** | SE除去（高速版） | 中速 | 高 |
| **D** | ノイズ除去のみ | 速い | 中 |
| **0** | 標準品質向上 | 中速 | 高 |

**迷ったら**: Mode S

---

## よくある質問

### Q: どのモードを使えばいい？

**A**: 
- **ドアの音、足音、拍手などを除去したい** → Mode S
- **速度重視** → Mode D または Mode 0
- **SE除去だけ** → Mode A

### Q: 処理時間はどのくらい？

**A**: 
- 1分の音声 → 2-3分（Mode S）
- 5分の音声 → 10-15分（Mode S）
- 10分の音声 → 20-30分（Mode S）

### Q: エラーが出た

**A**: 
1. `SE_REMOVAL_STATUS.md`のトラブルシューティングを確認
2. それでも解決しない場合は`SETUP_INSTRUCTIONS.md`の詳細手順へ

### Q: インストールに失敗した

**A**: 
```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "torch>=2.0.0,<3.0.0" "torchaudio>=2.0.0,<2.9.0"
pip install -r requirements_pro.txt
pip install "git+https://github.com/Audio-AGI/AudioSep.git"
pip install "speechbrain>=0.5.16"
```

---

## トラブルシューティング（超簡易版）

### エラー: `No module named 'pipeline'`
```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "git+https://github.com/Audio-AGI/AudioSep.git"
```

### エラー: `list_audio_backends`
```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "torchaudio<2.9.0" --force-reinstall
```

### 処理が遅すぎる
→ 正常です。Mode DまたはMode 0を試してください。

---

## 次に読むべきドキュメント

- 詳細な使い方: `README_PRO.md`
- セットアップ詳細: `SETUP_INSTRUCTIONS.md`
- SE除去の仕組み: `SE_REMOVAL_STATUS.md`

---

**これだけ覚えればOK**:
```bash
cd ~/HotDoc/AudioCleaner
./audio_cleaner_pro.command
# ファイルをドラッグ
# 'S' を入力
# 待つ
# 完了！
```


