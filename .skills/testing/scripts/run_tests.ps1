# Run all tests with coverage report
# Usage: .\scripts\run_tests.ps1

Write-Host "Running tests..." -ForegroundColor Cyan

uv run pytest tests/ -v --tb=short `
    --cov=services `
    --cov=ingestion `
    --cov=retrieval `
    --cov-report=term-missing

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll tests passed." -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed." -ForegroundColor Red
    exit 1
}
