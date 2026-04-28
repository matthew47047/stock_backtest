param(
    [string]$Ticker,
    [string[]]$Tickers,
    [double[]]$Weights,
    [Parameter(Mandatory = $true)]
    [string]$Start,
    [Parameter(Mandatory = $true)]
    [string]$End,
    [double]$Capital = 1000000,
    [int]$ShortWindow = 5,
    [int]$LongWindow = 20
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "No .venv found. Creating virtual environment..."
    python -m venv (Join-Path $projectRoot ".venv")
}

Write-Host "Installing/updating dependencies..."
& $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")

$mainPy = Join-Path $projectRoot "main.py"
$argsList = @(
    $mainPy,
    "--start", $Start,
    "--end", $End,
    "--capital", $Capital,
    "--short-window", $ShortWindow,
    "--long-window", $LongWindow
)

if ($Tickers) {
    $joinedTickers = ($Tickers | ForEach-Object { "$_".Trim() } | Where-Object { $_ }) -join ","
    if (-not $joinedTickers) {
        throw "Tickers is empty after normalization."
    }
    $argsList += @("--tickers", $joinedTickers)

    if ($Weights) {
        $joinedWeights = ($Weights | ForEach-Object { "$_" }) -join ","
        $argsList += @("--weights", $joinedWeights)
    }
}
elseif ($Ticker) {
    $argsList += @("--ticker", $Ticker)
}
else {
    throw "Please provide either -Ticker or -Tickers."
}

Write-Host "Running backtest..."
& $venvPython @argsList
