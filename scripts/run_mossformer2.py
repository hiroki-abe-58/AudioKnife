#!/usr/bin/env python3
"""
MossFormer2 - Speech Separation Script
話者分離: 複数音声が混在した音源から特定話者を抽出

MossFormer2はTransformerとRNN-Free Recurrent Networkを組み合わせた
時間領域モナラル音声分離モデルです。

特徴:
- 長距離依存関係とファインスケールの再帰パターンを効果的にキャプチャ
- WSJ0-2/3mix, Libri2Mix, WHAM!/WHAMR!ベンチマークで優れた性能
"""

import os
import sys
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def setup_mossformer2():
    """MossFormer2モデルのセットアップ"""
    try:
        from modelscope.pipelines import pipeline
        from modelscope.utils.constant import Tasks
    except ImportError as e:
        print(f"[エラー] ModelScopeが見つかりません: {e}")
        print("インストール方法:")
        print("  pip install modelscope")
        print("")
        print("また、libsndfileが必要です:")
        print("  macOS: brew install libsndfile")
        print("  Ubuntu: sudo apt-get install libsndfile1")
        sys.exit(1)
    
    try:
        print("[情報] MossFormer2モデル読み込み中...")
        print("[情報] 初回実行時はモデルのダウンロードに時間がかかります")
        
        # MossFormer2音声分離パイプラインを初期化
        separation_pipeline = pipeline(
            Tasks.speech_separation,
            model='damo/speech_mossformer2_separation_temporal_8k'
        )
        
        print("[情報] モデル読み込み完了")
        return separation_pipeline
    except Exception as e:
        print(f"[エラー] モデル読み込み失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def load_audio_info(input_path):
    """音声ファイル情報を取得"""
    import soundfile as sf
    
    print(f"[処理中] {input_path} を読み込み中...")
    info = sf.info(input_path)
    print(f"[情報] 元の音声: {info.samplerate}Hz, {info.channels}ch, {info.duration:.2f}秒")
    
    return info


def resample_to_8k(input_path, temp_path):
    """音声を8kHzにリサンプル（MossFormer2の要件）"""
    import soundfile as sf
    import numpy as np
    
    try:
        import librosa
    except ImportError:
        print("[エラー] librosaが必要です: pip install librosa")
        sys.exit(1)
    
    # 音声読み込み
    audio, sr = librosa.load(input_path, sr=None, mono=True)
    
    # 8kHzにリサンプル
    if sr != 8000:
        print(f"[情報] リサンプリング中 ({sr}Hz -> 8000Hz)...")
        audio = librosa.resample(audio, orig_sr=sr, target_sr=8000)
    
    # 一時ファイルに保存
    sf.write(temp_path, audio, 8000, subtype='PCM_16')
    
    return sr  # 元のサンプリングレートを返す


def resample_from_8k(audio_8k, original_sr):
    """8kHzから元のサンプリングレートに戻す"""
    try:
        import librosa
    except ImportError:
        return audio_8k, 8000
    
    if original_sr != 8000:
        print(f"[情報] リサンプリング中 (8000Hz -> {original_sr}Hz)...")
        audio = librosa.resample(audio_8k.astype(float), orig_sr=8000, target_sr=original_sr)
        return audio, original_sr
    
    return audio_8k, 8000


def process_with_mossformer2(input_path, output_path, pipeline, speaker_index=0):
    """
    MossFormer2で音声を処理
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス
        pipeline: MossFormer2パイプライン
        speaker_index: 抽出する話者のインデックス（0または1）
    
    Returns:
        処理成功の場合True
    """
    import numpy as np
    import soundfile as sf
    import tempfile
    
    try:
        # 音声情報取得
        info = load_audio_info(input_path)
        original_sr = info.samplerate
        
        # 8kHzにリサンプルした一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_8k_path = tmp.name
        
        try:
            resample_to_8k(input_path, temp_8k_path)
            
            print("[処理中] MossFormer2音声分離中...")
            
            # MossFormer2で分離
            result = pipeline(temp_8k_path)
            
            # 結果を取得
            if 'output_pcm_list' in result:
                pcm_list = result['output_pcm_list']
                
                if len(pcm_list) == 0:
                    print("[エラー] 分離結果が空です")
                    return False
                
                # 指定された話者のPCMデータを取得
                if speaker_index >= len(pcm_list):
                    speaker_index = 0
                
                print(f"[情報] {len(pcm_list)}人の話者を検出、話者{speaker_index + 1}を抽出中...")
                
                # PCMデータをnumpy配列に変換
                audio_data = np.frombuffer(pcm_list[speaker_index], dtype=np.int16)
                
                # 元のサンプリングレートに戻す
                audio_float = audio_data.astype(np.float32) / 32768.0
                audio_resampled, final_sr = resample_from_8k(audio_float, original_sr)
                
                # 保存
                print(f"[保存中] {output_path} に保存中...")
                sf.write(output_path, audio_resampled, final_sr)
                print(f"[情報] 出力: {final_sr}Hz, 1ch")
                
                return True
            else:
                print("[エラー] 予期しない結果形式")
                return False
                
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_8k_path):
                os.unlink(temp_8k_path)
                
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_audio(input_path, output_path, speaker_index=0, save_all=False):
    """
    メイン処理関数
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス
        speaker_index: 抽出する話者のインデックス
        save_all: すべての話者を保存する場合True
    """
    import numpy as np
    import soundfile as sf
    import tempfile
    
    try:
        # モデルセットアップ
        pipeline = setup_mossformer2()
        
        # 音声情報取得
        info = load_audio_info(input_path)
        original_sr = info.samplerate
        
        # 8kHzにリサンプルした一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_8k_path = tmp.name
        
        try:
            resample_to_8k(input_path, temp_8k_path)
            
            print("[処理中] MossFormer2音声分離中...")
            
            # MossFormer2で分離
            result = pipeline(temp_8k_path)
            
            # 結果を取得
            if 'output_pcm_list' in result:
                pcm_list = result['output_pcm_list']
                
                if len(pcm_list) == 0:
                    print("[エラー] 分離結果が空です")
                    return False
                
                print(f"[情報] {len(pcm_list)}人の話者を検出")
                
                output_path = Path(output_path)
                
                if save_all:
                    # すべての話者を保存
                    for i, pcm in enumerate(pcm_list):
                        audio_data = np.frombuffer(pcm, dtype=np.int16)
                        audio_float = audio_data.astype(np.float32) / 32768.0
                        audio_resampled, final_sr = resample_from_8k(audio_float, original_sr)
                        
                        spk_output = output_path.parent / f"{output_path.stem}_speaker{i+1}{output_path.suffix}"
                        print(f"[保存中] 話者{i+1}: {spk_output}")
                        sf.write(str(spk_output), audio_resampled, final_sr)
                    
                    print(f"[完了] {len(pcm_list)}個のファイルを保存しました")
                else:
                    # 指定された話者のみ保存
                    if speaker_index >= len(pcm_list):
                        speaker_index = 0
                    
                    print(f"[情報] 話者{speaker_index + 1}を抽出中...")
                    
                    audio_data = np.frombuffer(pcm_list[speaker_index], dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    audio_resampled, final_sr = resample_from_8k(audio_float, original_sr)
                    
                    print(f"[保存中] {output_path} に保存中...")
                    sf.write(str(output_path), audio_resampled, final_sr)
                    print(f"[情報] 出力: {final_sr}Hz, 1ch")
                
                print("[完了] 処理完了!")
                return True
            else:
                print("[エラー] 予期しない結果形式")
                return False
                
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_8k_path):
                os.unlink(temp_8k_path)
                
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="MossFormer2 - 話者分離ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  基本的な使い方（話者1を抽出）:
    python run_mossformer2.py input.wav
    
  話者2を抽出:
    python run_mossformer2.py input.wav --speaker 1
    
  すべての話者を保存:
    python run_mossformer2.py input.wav --all
    
  出力ファイル指定:
    python run_mossformer2.py input.wav -o output.wav

特徴:
  - Transformer + RNN-Free構造
  - 複数話者の分離に対応
  - ノイズに混じった音声の抽出に効果的
"""
    )
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    parser.add_argument("-s", "--speaker", type=int, default=0,
                       help="抽出する話者のインデックス（0から開始、デフォルト: 0）")
    parser.add_argument("--all", action="store_true",
                       help="すべての話者を別々のファイルに保存")
    
    args = parser.parse_args()
    
    # 対話モード
    if not args.input:
        print("===== MossFormer2 - 話者分離ツール =====")
        print("")
        print("このツールは混合音声から話者を分離します:")
        print("  - 複数人の会話から特定話者を抽出")
        print("  - ノイズに混じった音声の抽出")
        print("  - BGM上の音声の抽出")
        print("")
        print("特徴:")
        print("  - Transformer + RNN-Free構造")
        print("  - 高精度な話者分離")
        print("")
        print("使い方:")
        print("  1. 音声ファイルをこのウィンドウにドラッグ&ドロップ")
        print("  2. Enterキーを押す")
        print("")
        input_path = input("音声ファイルのパス: ").strip().strip("'\"")
        if not input_path:
            print("[エラー] ファイルパスが入力されていません")
            sys.exit(1)
    else:
        input_path = args.input
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"[エラー] ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    # 出力パス
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_separated.wav"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    if args.all:
        print("モード: すべての話者を保存")
    else:
        print(f"話者: {args.speaker + 1}")
    print("")
    
    success = process_audio(
        str(input_path), 
        str(output_path),
        speaker_index=args.speaker,
        save_all=args.all
    )
    
    if success:
        print(f"\n結果ファイル: {output_path}")
        print("完了!")
    else:
        print("\n処理失敗")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[中断] Ctrl+Cで中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"[エラー] 予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
