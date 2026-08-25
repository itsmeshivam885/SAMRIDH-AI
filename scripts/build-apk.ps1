# SAMRIDH-AI APK Builder Script for Android
param (
    [switch]$OpenAndroidStudio = $false
)

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "  SAMRIDH-AI | Android APK Builder (Team TwinBit)" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green

$RootPath = Resolve-Path "$PSScriptRoot\.."

Set-Location $RootPath

# Step 1: Check Node.js & npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Node.js / npm is required to bundle the Android APK." -ForegroundColor Red
    Write-Host "    Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Initializing Capacitor Android wrapper..." -ForegroundColor Cyan
if (-not (Test-Path "$RootPath\package.json")) {
    npm init -y
}

# Install Capacitor packages if missing
Write-Host "[+] Ensuring @capacitor/core, @capacitor/cli, @capacitor/android..." -ForegroundColor Cyan
npm install --save @capacitor/core @capacitor/android @capacitor/cli

# Create capacitor.config.json
$capConfig = @{
    appId = "gov.in.pmfby.samridhai"
    appName = "SAMRIDH-AI"
    webDir = "apps/web"
    server = @{
        androidScheme = "https"
        cleartext = $true
    }
} | ConvertTo-Json -Depth 4

Set-Content -Path "$RootPath\capacitor.config.json" -Value $capConfig
Write-Host "[+] Created capacitor.config.json" -ForegroundColor Green

# Add Android Platform
if (-not (Test-Path "$RootPath\android")) {
    Write-Host "[+] Adding Android native project..." -ForegroundColor Cyan
    npx cap add android
} else {
    Write-Host "[+] Syncing latest web build to Android project..." -ForegroundColor Cyan
    npx cap sync android
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "  Android Native Project Ready at: .\android" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To generate the .APK file:" -ForegroundColor Yellow
Write-Host "1. In Android Studio:" -ForegroundColor White
Write-Host "   Run: npx cap open android" -ForegroundColor Cyan
Write-Host "   Click 'Build' -> 'Build Bundle(s) / APK(s)' -> 'Build APK(s)'" -ForegroundColor White
Write-Host ""
Write-Host "2. Or CLI Gradle direct build:" -ForegroundColor White
Write-Host "   cd android; .\gradlew assembleDebug" -ForegroundColor Cyan
Write-Host "   The APK will be generated at: android\app\build\outputs\apk\debug\app-debug.apk" -ForegroundColor Green
Write-Host ""

if ($OpenAndroidStudio) {
    npx cap open android
}
