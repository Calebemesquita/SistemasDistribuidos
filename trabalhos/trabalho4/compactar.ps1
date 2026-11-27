$saida = Join-Path (Get-Location) 'projeto.zip'
$arquivos = Get-ChildItem -Recurse -File | Where-Object {
  $_.Name -ne 'projeto.zip' -and
  $_.FullName -notmatch '[\\/](node_modules|\.git|\.venv|__pycache__)([\\/]|$)'
}

Compress-Archive -Path $arquivos.FullName -DestinationPath $saida -Force
