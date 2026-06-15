# ============================================
# setup_scheduled_task.ps1
# Register Windows scheduled task: 20:00 daily ETF batch
# Run as Administrator
# ============================================

$TaskName = "ETF-Daily-Batch"
$ScriptPath = "D:\ETF-Platform\run_daily.bat"
$WorkingDir = "D:\ETF-Platform"
$LogDir = "D:\ETF-Platform\logs"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Deleting existing task: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Trigger = New-ScheduledTaskTrigger -Daily -At 20:00

# Simple action: just call the bat file (bat handles all logging internally)
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c D:\ETF-Platform\run_daily.bat" `
    -WorkingDirectory $WorkingDir

$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable
$Settings.DisallowStartIfOnBatteries = $false
$Settings.StopIfGoingOnBatteries = $false

$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Principal $Principal `
    -Description "ETF Platform Daily Batch - 20:00"

Write-Host ""
Write-Host "[OK] Scheduled task registered: $TaskName"
Write-Host "     Runs daily at 20:00"
Write-Host "     Logs: $LogDir"