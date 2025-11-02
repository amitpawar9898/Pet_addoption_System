# start_mysql.ps1
# Attempts to start common MySQL services or XAMPP MySQL.
# Run as Administrator.

Write-Host "Attempting to start MySQL services..."

$servicesToTry = @('MySQL80','MySQL','mysql')
$started = $false

foreach ($svc in $servicesToTry) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        Write-Host "Found service: $($s.Name) - Status: $($s.Status)"
        if ($s.Status -ne 'Running') {
            try {
                Start-Service -Name $s.Name -ErrorAction Stop
                Write-Host "Started service: $($s.Name)"
                $started = $true
                break
            } catch {
                Write-Host "Failed to start $($s.Name): $_"
            }
        } else {
            Write-Host "Service already running: $($s.Name)"
            $started = $true
            break
        }
    }
}

if (-not $started) {
    # Try starting XAMPP control panel (if installed)
    $xamppPath = 'C:\xampp\xampp-control.exe'
    if (Test-Path $xamppPath) {
        Write-Host "XAMPP detected at $xamppPath - launching control panel..."
        Start-Process -FilePath $xamppPath
        Write-Host "Open XAMPP control panel and start MySQL from there."
    } else {
        Write-Host "No XAMPP detected. If MySQL is not installed, install XAMPP or MySQL Server."
    }
}

Write-Host "Done. Check service status with: Get-Service *mysql* | Format-Table Name, Status -AutoSize"}