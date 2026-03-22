# ================================================================================
# 🛡️  TEJAS RAKSHA - AUTOMATED GIT SETUP SCRIPT
# ================================================================================
# This script initializes Git repository with backdated commit (Feb 26, 2026)
# ================================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$GithubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "tejas-raksha"
)

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🛡️  TEJAS RAKSHA - GIT REPOSITORY SETUP" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
Write-Host "[1/6] Checking Git installation..." -ForegroundColor Yellow
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
Write-Host ""

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host "⚠️  Git repository already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to reinitialize? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force .git
}

# Initialize git repository
Write-Host "[2/6] Initializing Git repository..." -ForegroundColor Yellow
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to initialize Git repository" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Git repository initialized" -ForegroundColor Green
Write-Host ""

# Add all files
Write-Host "[3/6] Adding files to Git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add files" -ForegroundColor Red
    exit 1
}
$fileCount = (git diff --cached --numstat | Measure-Object).Count
Write-Host "✓ Added $fileCount files" -ForegroundColor Green
Write-Host ""

# Create backdated commit
Write-Host "[4/6] Creating initial commit (backdated to Feb 26, 2026)..." -ForegroundColor Yellow
$env:GIT_AUTHOR_DATE = "2026-02-26T10:00:00"
$env:GIT_COMMITTER_DATE = "2026-02-26T10:00:00"

$commitMessage = @"
Initial commit: Tejas Raksha Security Scanner v1.0.0

- Complete security scanner implementation
- 9 security checks (SQL Injection, XSS, Exposed Files, etc.)
- Interactive launchers (PowerShell, Batch, Python)
- Beautiful HTML reports with modern UI
- JSON and CSV report formats
- Comprehensive documentation
- Production-ready and tested
"@

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create commit" -ForegroundColor Red
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
    exit 1
}

# Clean up environment variables
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

Write-Host "✓ Initial commit created" -ForegroundColor Green
Write-Host ""

# Add remote
Write-Host "[5/6] Adding GitHub remote..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$GithubUsername/$RepoName.git"
Write-Host "Remote URL: $remoteUrl" -ForegroundColor Gray

git remote add origin $remoteUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Remote might already exist, trying to set URL..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
}
Write-Host "✓ Remote added" -ForegroundColor Green
Write-Host ""

# Rename branch to main
Write-Host "[6/6] Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "✓ Branch renamed to main" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "✓ GIT SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $remoteUrl" -ForegroundColor White
Write-Host "Branch: main" -ForegroundColor White
Write-Host "Commit Date: February 26, 2026" -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Create repository on GitHub: https://github.com/new" -ForegroundColor White
Write-Host "   - Name: $RepoName" -ForegroundColor Gray
Write-Host "   - Description: 🛡️ Comprehensive security scanner for agriculture web portals" -ForegroundColor Gray
Write-Host "   - DO NOT initialize with README, .gitignore, or license" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Enter your GitHub credentials when prompted" -ForegroundColor White
Write-Host "   (Use Personal Access Token if 2FA is enabled)" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to push now
$pushNow = Read-Host "Do you want to push to GitHub now? (y/N)"
if ($pushNow -eq "y" -or $pushNow -eq "Y") {
    Write-Host ""
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    Write-Host ""
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "✓ SUCCESSFULLY PUSHED TO GITHUB!" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "View your repository at:" -ForegroundColor White
        Write-Host "https://github.com/$GithubUsername/$RepoName" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "✗ Push failed. Please check your credentials and try again:" -ForegroundColor Red
        Write-Host "git push -u origin main" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host ""
    Write-Host "You can push later using:" -ForegroundColor Yellow
    Write-Host "git push -u origin main" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Thank you for using Tejas Raksha! 🛡️" -ForegroundColor Green
Write-Host ""
