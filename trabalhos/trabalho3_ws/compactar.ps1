$excluir = @('node_modules', '.git', 'dist', '.env', '.vscode', 'compactar.ps1', 'projeto.zip', '__pycache__', '.venv')

Get-ChildItem -Recurse -File |
  Where-Object {
    $caminho = $_.FullName
    -not ($excluir | Where-Object { $caminho -like "*\$_\*" -or $_.Name -eq $_ })
  } |
  Compress-Archive -DestinationPath projeto.zip