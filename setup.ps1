# -----------------------------
# Create Directories
# -----------------------------

$Directories = @(
    "app",
    "app\api",
    "app\api\routes",
    "app\core",
    "app\models",
    "app\schemas",
    "app\services",
    "app\templates",
    "app\static",
    "app\static\css",
    "app\static\js",
    "app\static\images",
    "tests",
    "docs"
)

foreach ($Directory in $Directories) {

    if (-not (Test-Path -Path $Directory -PathType Container)) {
        New-Item -ItemType Directory -Path $Directory | Out-Null
        Write-Host "[+] Created folder: $Directory" -ForegroundColor Green
    }
    else {
        Write-Host "[=] Folder already exists: $Directory" -ForegroundColor Yellow
    }
}


# -----------------------------
# Create Python __init__.py
# -----------------------------

$PythonFiles = @(
    "app\__init__.py",
    "app\api\__init__.py",
    "app\api\routes\__init__.py",
    "app\core\__init__.py",
    "app\models\__init__.py",
    "app\schemas\__init__.py",
    "app\services\__init__.py"
)

foreach ($File in $PythonFiles) {

    if (-not (Test-Path -Path $File -PathType Leaf)) {
        New-Item -ItemType File -Path $File | Out-Null
        Write-Host "[+] Created file:   $File" -ForegroundColor Green
    }
    else {
        Write-Host "[=] File already exists: $File" -ForegroundColor Yellow
    }
}


# -----------------------------
# Done
# -----------------------------

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " LinuxLabX structure is ready!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Show structure if tree command is available
if (Get-Command tree -ErrorAction SilentlyContinue) {
    tree /F
}
else {
    Get-ChildItem -Recurse
}
