param(
    [Parameter(Mandatory = $true)][string]$PdfPath,
    [Parameter(Mandatory = $true)][int[]]$Pages,
    [string]$OutputDirectory = ".local\pdf-review"
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType=WindowsRuntime]
$operationBridge = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1
} | Select-Object -First 1
$actionBridge = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1
} | Select-Object -First 1
function Get-PdfOperationResult($operation, [Type]$resultType) {
    $task = $operationBridge.MakeGenericMethod($resultType).Invoke($null, @($operation))
    $task.Wait()
    return $task.Result
}
$source = (Resolve-Path -LiteralPath $PdfPath).Path
$file = Get-PdfOperationResult ([Windows.Storage.StorageFile]::GetFileFromPathAsync($source)) ([Windows.Storage.StorageFile])
$document = Get-PdfOperationResult ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$destination = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $OutputDirectory))
$null = New-Item -ItemType Directory -Path $destination -Force
foreach ($number in $Pages) {
    if ($number -lt 1 -or $number -gt $document.PageCount) { throw "Pagina fora do PDF: $number" }
    $page = $document.GetPage($number - 1)
    $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
    $render = $actionBridge.Invoke($null, @($page.RenderToStreamAsync($stream)))
    $render.Wait()
    $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
    $null = Get-PdfOperationResult ($reader.LoadAsync([uint32]$stream.Size)) ([uint32])
    $bytes = New-Object byte[] ([int]$stream.Size)
    $reader.ReadBytes($bytes)
    $target = Join-Path $destination ("pagina-{0:D2}.png" -f $number)
    [System.IO.File]::WriteAllBytes($target, $bytes)
    $page.Dispose()
    $reader.Dispose()
    $stream.Dispose()
    Write-Output $target
}
