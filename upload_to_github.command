#!/bin/bash

# ============================================================
# AudioKnife - GitHub Upload Script
# ============================================================
# This script uploads the project to GitHub using the personal account.
# Double-click to run or execute from terminal.
# 
# Repository: git@github.com:hiroki-abe-58/AudioKnife.git
# Account: hiroki-abe-58 (Personal)
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
REPO_URL="git@github.com:hiroki-abe-58/AudioKnife.git"
PERSONAL_NAME="hiroki-abe-58"
PERSONAL_EMAIL="hiroki-abe-58@users.noreply.github.com"

# Forbidden patterns (work account)
FORBIDDEN_NAME="fujigames"
FORBIDDEN_EMAIL="fujigames"

clear

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}    AudioKnife - GitHub Upload Script                       ${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}[INFO]${NC} Project directory: $SCRIPT_DIR"
echo ""

# ============================================================
# Pre-flight Checks
# ============================================================

echo -e "${YELLOW}[STEP 1/7]${NC} Running pre-flight checks..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Git is not installed. Please install Git first."
    read -p "Press Enter to exit..."
    exit 1
fi
echo -e "  ${GREEN}+${NC} Git is installed"

# Check SSH connection to GitHub (personal account)
echo -e "  ${BLUE}...${NC} Testing SSH connection to GitHub..."
SSH_RESULT=$(ssh -T git@github.com 2>&1)
if echo "$SSH_RESULT" | grep -q "Hi $PERSONAL_NAME"; then
    echo -e "  ${GREEN}+${NC} SSH authenticated as: ${GREEN}$PERSONAL_NAME${NC} (Personal Account)"
elif echo "$SSH_RESULT" | grep -qi "$FORBIDDEN_NAME"; then
    echo -e "${RED}[ERROR]${NC} Wrong account detected!"
    echo -e "${RED}        Currently authenticated as work account.${NC}"
    echo -e "${YELLOW}        Please check your SSH configuration.${NC}"
    echo ""
    echo -e "Expected: github.com -> Personal Account ($PERSONAL_NAME)"
    echo -e "Current SSH config should use: ~/.ssh/id_rsa for github.com"
    read -p "Press Enter to exit..."
    exit 1
else
    echo -e "  ${YELLOW}!${NC} SSH test result: $SSH_RESULT"
    echo -e "  ${YELLOW}!${NC} Continuing anyway (may work for first push)..."
fi

echo ""

# ============================================================
# Git Repository Setup
# ============================================================

echo -e "${YELLOW}[STEP 2/7]${NC} Setting up Git repository..."

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo -e "  ${BLUE}...${NC} Initializing new Git repository..."
    git init
    echo -e "  ${GREEN}+${NC} Git repository initialized"
else
    echo -e "  ${GREEN}+${NC} Git repository already exists"
fi

echo ""

# ============================================================
# Configure Git User (Local to this repo)
# ============================================================

echo -e "${YELLOW}[STEP 3/7]${NC} Configuring Git user (local to this repository)..."

# Set local git config to personal account
git config user.name "$PERSONAL_NAME"
git config user.email "$PERSONAL_EMAIL"

echo -e "  ${GREEN}+${NC} user.name  = $PERSONAL_NAME"
echo -e "  ${GREEN}+${NC} user.email = $PERSONAL_EMAIL"

# Double-check: Verify no work account traces in config
CURRENT_NAME=$(git config user.name)
CURRENT_EMAIL=$(git config user.email)

if echo "$CURRENT_NAME" | grep -qi "$FORBIDDEN_NAME" || echo "$CURRENT_EMAIL" | grep -qi "$FORBIDDEN_NAME"; then
    echo -e "${RED}[ERROR]${NC} Work account detected in git config!"
    echo -e "${RED}        Name: $CURRENT_NAME${NC}"
    echo -e "${RED}        Email: $CURRENT_EMAIL${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""

# ============================================================
# Setup Remote
# ============================================================

echo -e "${YELLOW}[STEP 4/7]${NC} Configuring remote repository..."

# Check if origin exists
if git remote | grep -q "^origin$"; then
    CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
        echo -e "  ${YELLOW}!${NC} Updating remote URL..."
        git remote set-url origin "$REPO_URL"
    fi
    echo -e "  ${GREEN}+${NC} Remote 'origin' configured: $REPO_URL"
else
    echo -e "  ${BLUE}...${NC} Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
    echo -e "  ${GREEN}+${NC} Remote 'origin' added: $REPO_URL"
fi

echo ""

# ============================================================
# Check for Sensitive Information
# ============================================================

echo -e "${YELLOW}[STEP 5/7]${NC} Checking for sensitive information..."

SENSITIVE_FOUND=0

# Check for files that should not be committed
SENSITIVE_PATTERNS=(
    ".env"
    "*.pem"
    "*.key"
    "id_rsa*"
    "credentials.json"
    "secrets.yaml"
    "api_keys.txt"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if find . -name "$pattern" -not -path "./.git/*" -not -path "./venv/*" 2>/dev/null | grep -q .; then
        echo -e "  ${YELLOW}!${NC} Found files matching: $pattern"
        SENSITIVE_FOUND=1
    fi
done

# Check if venv would be included (should be gitignored)
if [ -d "venv" ] && ! grep -q "^venv/" .gitignore 2>/dev/null; then
    echo -e "  ${RED}!${NC} WARNING: venv/ directory exists but may not be gitignored!"
    SENSITIVE_FOUND=1
fi

if [ $SENSITIVE_FOUND -eq 0 ]; then
    echo -e "  ${GREEN}+${NC} No sensitive files detected outside .gitignore"
else
    echo -e "  ${YELLOW}!${NC} Some potentially sensitive patterns found, but should be covered by .gitignore"
fi

# Show .gitignore status
if [ -f ".gitignore" ]; then
    echo -e "  ${GREEN}+${NC} .gitignore file exists"
else
    echo -e "  ${RED}!${NC} WARNING: No .gitignore file found!"
    read -p "Press Enter to continue anyway, or Ctrl+C to cancel..."
fi

echo ""

# ============================================================
# Stage and Commit Changes
# ============================================================

echo -e "${YELLOW}[STEP 6/7]${NC} Staging and committing changes..."

# Add all files
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo -e "  ${BLUE}...${NC} No new changes to commit"
    
    # Check if there are any commits
    if ! git rev-parse HEAD &>/dev/null 2>&1; then
        echo -e "  ${YELLOW}!${NC} No commits yet. Creating initial commit..."
        git commit -m "Initial commit: AudioKnife - AI-Powered Audio Enhancement Tool"
        echo -e "  ${GREEN}+${NC} Initial commit created"
    fi
else
    # Get commit message from user or use default
    echo ""
    echo -e "  ${CYAN}Enter commit message (or press Enter for auto-generated message):${NC}"
    read -r USER_MESSAGE
    
    if [ -z "$USER_MESSAGE" ]; then
        # Auto-generate commit message
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        COMMIT_MESSAGE="Update: $TIMESTAMP"
        
        # Try to make a more descriptive message
        CHANGED_FILES=$(git diff --cached --name-only | head -3)
        if [ -n "$CHANGED_FILES" ]; then
            FIRST_FILE=$(echo "$CHANGED_FILES" | head -1)
            NUM_FILES=$(git diff --cached --name-only | wc -l | tr -d ' ')
            if [ "$NUM_FILES" -eq 1 ]; then
                COMMIT_MESSAGE="Update: $FIRST_FILE"
            else
                COMMIT_MESSAGE="Update: $FIRST_FILE and $((NUM_FILES - 1)) other file(s)"
            fi
        fi
    else
        COMMIT_MESSAGE="$USER_MESSAGE"
    fi
    
    git commit -m "$COMMIT_MESSAGE"
    echo -e "  ${GREEN}+${NC} Changes committed: $COMMIT_MESSAGE"
fi

echo ""

# ============================================================
# Push to GitHub
# ============================================================

echo -e "${YELLOW}[STEP 7/7]${NC} Pushing to GitHub..."

# Determine the current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)

if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    git branch -M main
fi

echo -e "  ${BLUE}...${NC} Current branch: $CURRENT_BRANCH"
echo -e "  ${BLUE}...${NC} Pushing to origin/$CURRENT_BRANCH..."

# Push with upstream tracking
if git push -u origin "$CURRENT_BRANCH" 2>&1; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}    SUCCESS! Project uploaded to GitHub                     ${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "  Repository: ${BLUE}https://github.com/hiroki-abe-58/AudioKnife${NC}"
    echo -e "  Branch:     ${BLUE}$CURRENT_BRANCH${NC}"
    echo -e "  Account:    ${BLUE}$PERSONAL_NAME${NC} (Personal)"
    echo ""
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}    FAILED! Could not push to GitHub                        ${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo -e "Please check:"
    echo -e "  1. SSH key is correctly configured for github.com"
    echo -e "  2. You have write access to the repository"
    echo -e "  3. The repository exists on GitHub"
    echo ""
    echo -e "To create the repository on GitHub:"
    echo -e "  1. Go to https://github.com/new"
    echo -e "  2. Repository name: AudioKnife"
    echo -e "  3. Make sure you're logged in as: $PERSONAL_NAME"
    echo ""
fi

echo -e "${CYAN}------------------------------------------------------------${NC}"
read -p "Press Enter to close..."
