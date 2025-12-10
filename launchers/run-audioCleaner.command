#!/bin/bash

# ============================================================================
# AudioCleaner Launcher
# ダブルクリックで起動し、必要に応じて自動インストールを実行
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# スクリプトのディレクトリに移動
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

clear

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    AudioCleaner Launcher             ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# インストール状態チェック
# ============================================================================

check_installation() {
    local all_ok=true
    
    echo -e "${BLUE}インストール状態を確認中...${NC}"
    echo ""
    
    # 1. Python確認
    echo -n "  [1/5] Python 3... "
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
    else
        echo -e "${RED}✗ 未インストール${NC}"
        all_ok=false
    fi
    
    # 2. 仮想環境確認
    echo -n "  [2/5] 仮想環境... "
    if [ -d "venv" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
    else
        echo -e "${YELLOW}✗ 未作成${NC}"
        all_ok=false
    fi
    
    # 3. 基本依存関係確認
    echo -n "  [3/5] 基本依存関係... "
    if [ -d "venv" ]; then
        source venv/bin/activate
        if python3 -c "import torch, torchaudio" 2>/dev/null; then
            echo -e "${GREEN}✓ インストール済み${NC}"
        else
            echo -e "${YELLOW}✗ 未インストール${NC}"
            all_ok=false
        fi
        deactivate 2>/dev/null
    else
        echo -e "${YELLOW}✗ スキップ${NC}"
        all_ok=false
    fi
    
    # 4. Denoiser確認
    echo -n "  [4/5] Denoiser... "
    if [ -f "scripts/run_clearSound.py" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
    else
        echo -e "${YELLOW}✗ 未配置${NC}"
        all_ok=false
    fi
    
    # 5. メインスクリプト確認
    echo -n "  [5/5] メインスクリプト... "
    if [ -f "audio_cleaner.command" ] || [ -f "audio_cleaner_pro.command" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
    else
        echo -e "${RED}✗ 未配置${NC}"
        all_ok=false
    fi
    
    echo ""
    
    if [ "$all_ok" = true ]; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# 自動インストール
# ============================================================================

auto_install() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  セットアップが必要です${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "AudioCleanerを使用するには、初回セットアップが必要です。"
    echo "以下がインストールされます："
    echo ""
    echo "  • Python仮想環境"
    echo "  • PyTorch & TorchAudio"
    echo "  • 音声処理ライブラリ"
    echo "  • AIモデル（約3-4GB）"
    echo ""
    echo "処理時間：約5-10分"
    echo "インターネット接続が必要です。"
    echo ""
    
    read -p "今すぐセットアップを実行しますか？ [Y/n]: " response
    
    if [[ "$response" =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}セットアップをキャンセルしました。${NC}"
        echo "後でセットアップする場合は、以下を実行してください："
        echo "  ./install.sh"
        echo ""
        read -p "Enterキーで終了..."
        exit 0
    fi
    
    echo ""
    echo -e "${GREEN}━━━ セットアップを開始します ━━━${NC}"
    echo ""
    
    # インストールスクリプトを実行
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}  セットアップ完了！${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            read -p "Enterキーで AudioCleaner を起動..."
            return 0
        else
            echo ""
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${RED}  セットアップに失敗しました${NC}"
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "手動でインストールを試してください："
            echo "  ./install.sh"
            echo ""
            read -p "Enterキーで終了..."
            exit 1
        fi
    else
        echo -e "${RED}エラー: install.sh が見つかりません${NC}"
        read -p "Enterキーで終了..."
        exit 1
    fi
}

# ============================================================================
# バージョン選択
# ============================================================================

select_version() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  AudioCleaner バージョン選択${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    local has_standard=false
    local has_pro=false
    
    if [ -f "audio_cleaner.command" ]; then
        has_standard=true
    fi
    
    if [ -f "audio_cleaner_pro.command" ]; then
        has_pro=true
    fi
    
    if [ "$has_standard" = true ] && [ "$has_pro" = true ]; then
        echo -e "${GREEN}1${NC}. AudioCleaner 標準版"
        echo "   • ノイズ除去（Denoiser）"
        echo "   • 音質向上（VoiceFixer）"
        echo "   • 高速処理"
        echo ""
        echo -e "${GREEN}2${NC}. AudioCleaner PRO"
        echo "   • SE（効果音）除去機能"
        echo "   • AudioSep統合"
        echo "   • SepFormer-DNS統合"
        echo "   • 最高品質（処理時間長め）"
        echo ""
        echo -e "${PURPLE}Q${NC}. 終了"
        echo ""
        
        read -p "選択 [1/2/Q]: " version_choice
        
        case $version_choice in
            1)
                return 1  # 標準版
                ;;
            2)
                # PRO版の依存関係チェック
                if [ -d "venv" ]; then
                    source venv/bin/activate
                    if python3 -c "import speechbrain" 2>/dev/null && python3 -c "from audiosep import AudioSep" 2>/dev/null; then
                        deactivate 2>/dev/null
                        return 2  # PRO版
                    else
                        deactivate 2>/dev/null
                        echo ""
                        echo -e "${YELLOW}PRO版の依存関係が不足しています。${NC}"
                        echo "PRO版をインストールしますか？"
                        echo ""
                        read -p "[Y/n]: " install_pro
                        
                        if [[ ! "$install_pro" =~ ^[Nn]$ ]]; then
                            if [ -f "install_pro.sh" ]; then
                                chmod +x install_pro.sh
                                ./install_pro.sh
                                return 2
                            else
                                echo -e "${RED}install_pro.sh が見つかりません${NC}"
                                read -p "標準版で起動しますか？ [Y/n]: " use_standard
                                if [[ ! "$use_standard" =~ ^[Nn]$ ]]; then
                                    return 1
                                else
                                    exit 0
                                fi
                            fi
                        else
                            echo "標準版で起動します..."
                            return 1
                        fi
                    fi
                fi
                ;;
            [Qq])
                echo "終了します"
                exit 0
                ;;
            *)
                echo -e "${YELLOW}無効な選択です。標準版で起動します。${NC}"
                sleep 1
                return 1
                ;;
        esac
    elif [ "$has_standard" = true ]; then
        echo "AudioCleaner 標準版で起動します..."
        sleep 1
        return 1
    elif [ "$has_pro" = true ]; then
        echo "AudioCleaner PRO版で起動します..."
        sleep 1
        return 2
    else
        echo -e "${RED}エラー: 実行可能なバージョンが見つかりません${NC}"
        exit 1
    fi
}

# ============================================================================
# メイン処理
# ============================================================================

main() {
    # インストール状態チェック
    if ! check_installation; then
        auto_install
    else
        echo -e "${GREEN}✓ インストール済み - すぐに起動できます${NC}"
        echo ""
    fi
    
    # バージョン選択
    select_version
    version=$?
    
    clear
    
    # 選択されたバージョンを起動
    case $version in
        1)
            if [ -f "audio_cleaner.command" ]; then
                chmod +x audio_cleaner.command
                exec ./audio_cleaner.command
            else
                echo -e "${RED}エラー: audio_cleaner.command が見つかりません${NC}"
                read -p "Enterキーで終了..."
                exit 1
            fi
            ;;
        2)
            if [ -f "audio_cleaner_pro.command" ]; then
                chmod +x audio_cleaner_pro.command
                exec ./audio_cleaner_pro.command
            else
                echo -e "${RED}エラー: audio_cleaner_pro.command が見つかりません${NC}"
                read -p "Enterキーで終了..."
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}エラー: 無効なバージョンです${NC}"
            read -p "Enterキーで終了..."
            exit 1
            ;;
    esac
}

# エラートラップ
trap 'echo -e "\n${RED}エラーが発生しました${NC}"; read -p "Enterキーで終了..."; exit 1' ERR

# メイン処理実行
main

