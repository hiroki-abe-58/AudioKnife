#!/usr/bin/env python3

import os
import sys
import torch
import torchaudio
from pathlib import Path
import argparse
import warnings
warnings.filterwarnings('ignore')

WORK_DIR = Path.home() / "clearSound"
sys.path.insert(0, str(WORK_DIR / "denoiser"))

def setup_model():
    try:
        from denoiser import pretrained
    except ImportError:
        print("[エラー] denoiserモジュールが見つからん")
        print("install_clearSound.command実行した？")
        sys.exit(1)
    
    model_path = WORK_DIR / "denoiser" / "pretrained" / "dns64.th"
    if not model_path.exists():
        print(f"[エラー] モデルファイルが見つからん: {model_path}")
        sys.exit(1)
    
    try:
        model = pretrained.dns64()
        model.eval()
        
        # MPSは一部のconvolution操作に対応していないため、CPUを使用
        device = torch.device("cpu")
        print("[情報] CPU使うで（安定動作優先）")
        
        model = model.to(device)
        return model, device
    except Exception as e:
        print(f"[エラー] モデル読み込み失敗: {e}")
        sys.exit(1)

def process_audio(input_path, output_path, model, device, high_quality=True):
    try:
        print(f"[処理中] {input_path} を読み込み中...")
        wav_original, sr_original = torchaudio.load(input_path)
        
        print(f"[情報] 元の音声: {sr_original}Hz, {wav_original.shape[0]}ch")
        
        is_stereo = wav_original.shape[0] > 1
        target_sr = 48000 if high_quality else 16000
        
        wav = wav_original.clone()
        
        if sr_original != model.sample_rate:
            print(f"[情報] モデル用にサンプリングレート変換中 ({sr_original}Hz → {model.sample_rate}Hz)...")
            resampler = torchaudio.transforms.Resample(sr_original, model.sample_rate)
            wav = resampler(wav)
        
        channels_processed = []
        
        if is_stereo:
            print("[情報] ステレオ音声を検出、各チャンネル個別処理するで...")
            for ch in range(min(wav.shape[0], 2)):
                print(f"  - チャンネル {ch+1} 処理中...")
                ch_wav = wav[ch:ch+1].unsqueeze(0).to(device)
                
                with torch.no_grad():
                    enhanced = model(ch_wav)
                
                if enhanced.dim() == 3:
                    enhanced = enhanced.squeeze(0)
                enhanced = enhanced.cpu()
                channels_processed.append(enhanced)
        else:
            print("[情報] モノラル音声を処理中...")
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)
            
            if wav.dim() == 2:
                wav = wav.unsqueeze(0)
            
            wav = wav.to(device)
            
            with torch.no_grad():
                enhanced = model(wav)
            
            if enhanced.dim() == 3:
                enhanced = enhanced.squeeze(0)
            enhanced = enhanced.cpu()
            channels_processed.append(enhanced)
        
        if is_stereo and len(channels_processed) == 2:
            enhanced_final = torch.cat(channels_processed, dim=0)
        else:
            enhanced_final = channels_processed[0]
        
        while enhanced_final.dim() > 2:
            enhanced_final = enhanced_final.squeeze(0)
        
        if enhanced_final.dim() == 1:
            enhanced_final = enhanced_final.unsqueeze(0)
        
        if high_quality and model.sample_rate != target_sr:
            print(f"[情報] 高音質化: {model.sample_rate}Hz → {target_sr}Hz に変換中...")
            resampler_up = torchaudio.transforms.Resample(model.sample_rate, target_sr)
            enhanced_final = resampler_up(enhanced_final)
        
        print(f"[情報] 最終出力: {target_sr}Hz, {enhanced_final.shape[0]}ch")
        print(f"[保存中] {output_path} に保存中...")
        torchaudio.save(output_path, enhanced_final, target_sr)
        
        print("[完了] ノイズ除去完了！")
        
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ガサガサ音源をキレイにするツール")
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    parser.add_argument("-q", "--quality", choices=["high", "normal"], default="high", 
                       help="出力音質 (high=48kHz, normal=16kHz)")
    args = parser.parse_args()
    
    if not args.input:
        print("===== 音源クリーンアップツール =====")
        print("使い方:")
        print("  1. 音声ファイルをこのウィンドウにドラッグ&ドロップ")
        print("  2. Enterキーを押す")
        print("")
        input_path = input("音声ファイルのパス: ").strip().strip("'\"")
        if not input_path:
            print("[エラー] ファイルパスが入力されてへん")
            sys.exit(1)
    else:
        input_path = args.input
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"[エラー] ファイルが見つからん: {input_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print(f"音質: {'高音質(48kHz)' if args.quality == 'high' else '標準(16kHz)'}")
    print("")
    
    model, device = setup_model()
    process_audio(str(input_path), str(output_path), model, device, 
                 high_quality=(args.quality == "high"))
    
    print(f"\n結果ファイル: {output_path}")
    print("おつかれさん！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[中断] Ctrl+Cで中断されたで")
        sys.exit(0)
    except Exception as e:
        print(f"[エラー] 予期せぬエラー: {e}")
        sys.exit(1)
