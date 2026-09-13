# Quartz Website Publish Script

Write-Host ""
Write-Host "====================================="
Write-Host "       Quartz Website Publish"
Write-Host "====================================="
Write-Host ""

# Check Quartz project
if (-not (Test-Path "quartz.config.yaml")) {
    Write-Host "ERROR: quartz.config.yaml not found."
    Write-Host "Please run this script in the Quartz project folder."
    exit 1
}

# Step 1: Build
Write-Host "[1/5] Building Quartz website..."
npx quartz build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Quartz build failed."
    Write-Host "Publish cancelled."
    exit 1
}

Write-Host ""
Write-Host "Build successful."

# Step 2: Git status
Write-Host ""
Write-Host "[2/5] Checking Git status..."
git status

# Step 3: Add files
Write-Host ""
Write-Host "[3/5] Adding changed files..."
git add .

# Check staged changes
$changes = git diff --cached --name-only

if ([string]::IsNullOrWhiteSpace(($changes -join ""))) {
    Write-Host ""
    Write-Host "No changes to publish."
    exit 0
}

# Ask for commit message
Write-Host ""
$message = Read-Host "Commit message"

if ([string]::IsNullOrWhiteSpace($message)) {
    $message = "Update website"
}

# Step 4: Commit
Write-Host ""
Write-Host "[4/5] Creating commit..."
git commit -m "$message"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Git commit failed."
    exit 1
}

# Step 5: Push
Write-Host ""
Write-Host "[5/5] Pushing to GitHub..."
git push origin v5

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Git push failed."
    exit 1
}

Write-Host ""
Write-Host "====================================="
Write-Host "       Publish completed!"
Write-Host "====================================="