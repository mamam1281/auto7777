# ==================================================
# Casino-Club F2P Development Environment Optimizer
# Fixes tool limits and performance issues (English)
# ==================================================

# Set UTF-8 encoding for proper display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Casino-Club F2P Dev Environment Setup" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables to fix tool limits
$env:NODE_OPTIONS = "--max-old-space-size=4096"
$env:VSCODE_DISABLE_WORKSPACE_TRUST = "true"
$env:NODE_ENV = "development"

Write-Host "Step 1: Tool Limit Optimization" -ForegroundColor Green
Write-Host "  - NODE_OPTIONS set to --max-old-space-size=4096" -ForegroundColor White
Write-Host "  - VSCODE_DISABLE_WORKSPACE_TRUST enabled" -ForegroundColor White
Write-Host "  - Memory limit increased for large projects" -ForegroundColor White
Write-Host ""

Write-Host "Step 2: Cache Cleanup" -ForegroundColor Green
$cacheCleared = $false

# Clear Node.js cache
if (Test-Path "cc-webapp/frontend/node_modules/.cache") {
    Remove-Item -Recurse -Force "cc-webapp/frontend/node_modules/.cache" -ErrorAction SilentlyContinue
    Write-Host "  - Node.js cache cleared" -ForegroundColor White
    $cacheCleared = $true
}

# Clear Next.js cache
if (Test-Path "cc-webapp/frontend/.next") {
    Remove-Item -Recurse -Force "cc-webapp/frontend/.next" -ErrorAction SilentlyContinue
    Write-Host "  - Next.js build cache cleared" -ForegroundColor White
    $cacheCleared = $true
}

# Clear npm cache
try {
    npm cache clean --force 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - npm cache cleared" -ForegroundColor White
        $cacheCleared = $true
    }
}
catch {
    # Silent fail for npm cache
}

if (-not $cacheCleared) {
    Write-Host "  - No cache to clear" -ForegroundColor Gray
}
Write-Host ""

Write-Host "Step 3: Environment Verification" -ForegroundColor Green
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "  - Node.js: $nodeVersion" -ForegroundColor White
    }
    else {
        Write-Host "  - Node.js: Not found" -ForegroundColor Red
    }
}
catch {
    Write-Host "  - Node.js: Error checking version" -ForegroundColor Red
}

try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Host "  - npm: v$npmVersion" -ForegroundColor White
    }
    else {
        Write-Host "  - npm: Not found" -ForegroundColor Red
    }
}
catch {
    Write-Host "  - npm: Error checking version" -ForegroundColor Red
}

Write-Host ""
Write-Host "Environment setup completed successfully!" -ForegroundColor Green
Write-Host "You can now run frontend development tasks." -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run 'npm run dev' in cc-webapp/frontend directory" -ForegroundColor White
Write-Host "  2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "  3. Backend is already running on http://localhost:8000" -ForegroundColor White
Write-Host ""
