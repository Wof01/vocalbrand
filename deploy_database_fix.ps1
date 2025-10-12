# 🚀 QUICK DEPLOYMENT SCRIPT
# Run this to deploy the database persistence fix

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  VOCALBRAND - DATABASE PERSISTENCE FIX" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "❌ Git repository not found!" -ForegroundColor Red
    Write-Host "Please run this script from the VOCALBRAND directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git repository found" -ForegroundColor Green
Write-Host ""

# Show what's changed
Write-Host "📋 Changes to be committed:" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow
git status --short
Write-Host ""

# Ask for confirmation
Write-Host "⚠️  This will:" -ForegroundColor Yellow
Write-Host "   1. Add PostgreSQL database for persistent storage" -ForegroundColor White
Write-Host "   2. Update authentication system" -ForegroundColor White
Write-Host "   3. Deploy to Render automatically" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Continue with deployment? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔄 Adding changes..." -ForegroundColor Cyan
git add .

Write-Host "📝 Creating commit..." -ForegroundColor Cyan
git commit -m "CRITICAL FIX: Add PostgreSQL for persistent user data storage

- Add db_adapter.py for database abstraction
- Update auth.py to support PostgreSQL and SQLite
- Add psycopg2-binary to requirements.txt
- Update render.yaml with PostgreSQL service
- Fix critical issue where user accounts were deleted on container restart
"

Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  ✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://dashboard.render.com" -ForegroundColor White
    Write-Host "   2. Wait 3-5 minutes for deployment" -ForegroundColor White
    Write-Host "   3. Verify 'vocalbrand-db' service is created" -ForegroundColor White
    Write-Host "   4. Test registration at: https://vocalbrand.onrender.com" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Read DATABASE_FIX_CRITICAL.md for full details" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host "Please check your Git credentials and try again" -ForegroundColor Yellow
    Write-Host ""
}
