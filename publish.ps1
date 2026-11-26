# Quartz Website Publish Script
# Run from the Quartz project directory. Supports Windows PowerShell 5.1+.

$ErrorActionPreference = 'Stop'
# Handle native exit codes explicitly, including git diff's expected code 1.
$PSNativeCommandUseErrorActionPreference = $false

try {
    Write-Host ""
    Write-Host "====================================="
    Write-Host "       Quartz Website Publish"
    Write-Host "====================================="
    Write-Host ""

    # Preflight checks
    if (-not (Test-Path -LiteralPath 'quartz.config.yaml' -PathType Leaf)) {
        throw 'quartz.config.yaml not found. Run this script in the Quartz project folder.'
    }
    foreach ($tool in @('git', 'npx')) {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            throw "$tool not found in PATH."
        }
    }

    $inside = git rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0 -or $inside -ne 'true') {
        throw 'Git repository not found. Restore the original .git directory before publishing.'
    }
    $root = git rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw 'Cannot determine Git repository root.' }
    if ((Resolve-Path -LiteralPath $root).Path -ne (Get-Location).Path) {
        throw 'Current folder is not the Git repository root.'
    }
    $branch = git branch --show-current
    if ($LASTEXITCODE -ne 0) { throw 'Cannot determine current Git branch.' }
    if ($branch -ne 'v5') { throw "Expected branch v5; current branch: '$branch'." }
    $remote = git remote get-url --push origin
    if ($LASTEXITCODE -ne 0 -or -not $remote) { throw 'Git remote origin is not configured.' }
    Write-Host "Branch: $branch"
    Write-Host "Remote: $remote"

    # Step 1: Build
    Write-Host "`n[1/5] Building Quartz website..."
    npx quartz build
    if ($LASTEXITCODE -ne 0) { throw 'Quartz build failed.' }
    Write-Host 'Build successful.' -ForegroundColor Green

    # Step 2: Git status
    Write-Host "`n[2/5] Checking Git status..."
    git status
    if ($LASTEXITCODE -ne 0) { throw 'Git status failed.' }

    # Step 3: Add files (same scope as original script)
    Write-Host "`n[3/5] Adding changed files..."
    git add .
    if ($LASTEXITCODE -ne 0) { throw 'Git add failed.' }

    git diff --cached --quiet --exit-code
    $diffExit = $LASTEXITCODE
    switch ($diffExit) {
        0 { Write-Host 'No staged changes.' }
        1 { Write-Host 'Staged changes detected.' }
        default { throw "Git diff failed (exit code $diffExit)." }
    }

    # Step 4: Commit only when there are staged changes
    Write-Host "`n[4/5] Creating commit..."
    if ($diffExit -eq 1) {
        foreach ($key in @('user.name', 'user.email')) {
            $identity = git config --get $key
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($identity -join ''))) {
                throw "Git $key is not configured. Set it with git config before retrying."
            }
        }
        $message = Read-Host 'Commit message'
        if ([string]::IsNullOrWhiteSpace($message)) { $message = 'Update website' }
        git commit -m "$message"
        if ($LASTEXITCODE -ne 0) { throw 'Git commit failed. Staged files are retained if the commit did not complete.' }
    } else {
        Write-Host 'No new commit required. Checking for pending push.'
    }

    # Step 5: Always check the live remote, even without staged changes.
    Write-Host "`n[5/5] Checking remote and pushing to GitHub..."
    Write-Host 'Complete GitHub sign-in in your browser if prompted.'
    git fetch origin refs/heads/v5:refs/remotes/origin/v5
    if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed. Check network or GitHub credentials; local commits are retained.' }

    $counts = git rev-list --left-right --count 'origin/v5...HEAD'
    if ($LASTEXITCODE -ne 0 -or ($counts -join '') -notmatch '^\s*\d+\s+\d+\s*$') {
        throw 'Cannot compare local and remote branches.'
    }
    $parts = ($counts -join '').Trim() -split '\s+'
    $behind = [long]$parts[0]
    $ahead = [long]$parts[1]
    Write-Host "Local commits ahead: $ahead; behind: $behind"

    if ($behind -gt 0) {
        throw 'Remote branch contains commits missing locally. Review and integrate them before publishing. No force push performed.'
    }
    if ($ahead -eq 0) {
        Write-Host 'No commits to push. Local and remote branches are synchronized.' -ForegroundColor Green
        exit 0
    }

    git push --verbose origin v5
    if ($LASTEXITCODE -ne 0) {
        throw 'Git push failed. Local commits are retained. Run pub again or git push --verbose origin v5.'
    }

    Write-Host "`n====================================="
    Write-Host '       Publish completed!' -ForegroundColor Green
    Write-Host '====================================='
    Write-Host 'GitHub upload successful. Check GitHub Actions for deployment status.'
    exit 0
} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Publish cancelled. No automatic reset or force push performed.'
    exit 1
}