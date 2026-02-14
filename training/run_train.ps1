$env:PYTHONUTF8 = "1"
$env:PYTHONUNBUFFERED = "1"
Set-Location "C:\data\devops.propercode.co.uk\ultimatelaw\training"
$logFile = "C:\data\devops.propercode.co.uk\ultimatelaw\training\train.log"
"Training started at $(Get-Date)" | Out-File $logFile
$proc = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-u","train_qlora.py","--model","qwen3-4b","--phase","1" -RedirectStandardOutput "$logFile.stdout" -RedirectStandardError "$logFile.stderr" -NoNewWindow -PassThru -Wait
"Training finished at $(Get-Date) with exit code $($proc.ExitCode)" | Out-File $logFile -Append
