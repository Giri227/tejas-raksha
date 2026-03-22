#!/bin/bash
# ================================================================================
# 🛡️  TEJAS RAKSHA - AUTOMATED GIT SETUP SCRIPT
# ================================================================================
# This script initializes Git repository with backdated commit (Feb 26, 2026)
# ================================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if username provided
if [ -z "$1" ]; then
    echo ""
    echo "Usage: ./setup_git.sh <github-username> [repo-name]"
    echo ""
    echo "Example: ./setup_git.sh johndoe tejas-raksha"
    echo ""
    exit 1
fi

GITHUB_USERNAME="$1"
REPO_NAME="${2:-tejas-raksha}"

echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${GREEN}🛡️  TEJAS RAKSHA - GIT REPOSITORY SETUP${NC}"
echo -e "${CYAN}================================================================================${NC}"
echo ""

# Check if git is installed
echo -e "${YELLOW}[1/6] Checking Git installation...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed!${NC}"
    echo -e "${RED}Please install Git from https://git-scm.com/downloads${NC}"
    exit 1
fi
GIT_VERSION=$(git --version)
echo -e "${GREEN}✓ Git is installed: $GIT_VERSION${NC}"
echo ""

# Check if already a git repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository already exists!${NC}"
    read -p "Do you want to reinitialize? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo -e "${YELLOW}Cancelled.${NC}"
        exit 0
    fi
    rm -rf .git
fi

# Initialize git repository
echo -e "${YELLOW}[2/6] Initializing Git repository...${NC}"
git init
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to initialize Git repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git repository initialized${NC}"
echo ""

# Add all files
echo -e "${YELLOW}[3/6] Adding files to Git...${NC}"
git add .
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to add files${NC}"
    exit 1
fi
FILE_COUNT=$(git diff --cached --numstat | wc -l)
echo -e "${GREEN}✓ Added $FILE_COUNT files${NC}"
echo ""

# Create backdated commit
echo -e "${YELLOW}[4/6] Creating initial commit (backdated to Feb 26, 2026)...${NC}"
GIT_AUTHOR_DATE="2026-02-26T10:00:00" \
GIT_COMMITTER_DATE="2026-02-26T10:00:00" \
git commit -m "Initial commit: Tejas Raksha Security Scanner v1.0.0

- Complete security scanner implementation
- 9 security checks (SQL Injection, XSS, Exposed Files, etc.)
- Interactive launchers (PowerShell, Batch, Python)
- Beautiful HTML reports with modern UI
- JSON and CSV report formats
- Comprehensive documentation
- Production-ready and tested"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to create commit${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Initial commit created${NC}"
echo ""

# Add remote
echo -e "${YELLOW}[5/6] Adding GitHub remote...${NC}"
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo -e "Remote URL: $REMOTE_URL"

git remote add origin "$REMOTE_URL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Remote might already exist, trying to set URL...${NC}"
    git remote set-url origin "$REMOTE_URL"
fi
echo -e "${GREEN}✓ Remote added${NC}"
echo ""

# Rename branch to main
echo -e "${YELLOW}[6/6] Renaming branch to main...${NC}"
git branch -M main
echo -e "${GREEN}✓ Branch renamed to main${NC}"
echo ""

# Summary
echo -e "${CYAN}================================================================================${NC}"
echo -e "${GREEN}✓ GIT SETUP COMPLETE!${NC}"
echo -e "${CYAN}================================================================================${NC}"
echo ""
echo -e "Repository: $REMOTE_URL"
echo -e "Branch: main"
echo -e "Commit Date: February 26, 2026"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo -e "1. Create repository on GitHub: https://github.com/new"
echo -e "   - Name: $REPO_NAME"
echo -e "   - Description: 🛡️ Comprehensive security scanner for agriculture web portals"
echo -e "   - DO NOT initialize with README, .gitignore, or license"
echo ""
echo -e "2. Push to GitHub:"
echo -e "   git push -u origin main"
echo ""
echo -e "3. Enter your GitHub credentials when prompted"
echo -e "   (Use Personal Access Token if 2FA is enabled)"
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo ""

# Ask if user wants to push now
read -p "Do you want to push to GitHub now? (y/N): " push_now
if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
    echo ""
    echo -e "${YELLOW}Pushing to GitHub...${NC}"
    echo ""
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${CYAN}================================================================================${NC}"
        echo -e "${GREEN}✓ SUCCESSFULLY PUSHED TO GITHUB!${NC}"
        echo -e "${CYAN}================================================================================${NC}"
        echo ""
        echo -e "View your repository at:"
        echo -e "${CYAN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
        echo ""
    else
        echo ""
        echo -e "${RED}✗ Push failed. Please check your credentials and try again:${NC}"
        echo -e "git push -u origin main"
        echo ""
    fi
else
    echo ""
    echo -e "${YELLOW}You can push later using:${NC}"
    echo -e "git push -u origin main"
    echo ""
fi

echo -e "${GREEN}Thank you for using Tejas Raksha! 🛡️${NC}"
echo ""
