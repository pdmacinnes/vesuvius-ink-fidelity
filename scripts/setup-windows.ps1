param([string]$Python = 'python', [switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
function Check-Exit { if ($LASTEXITCODE -ne 0) { throw "Command exited $LASTEXITCODE" } }
if (-not (Test-Path '.venv/Scripts/python.exe')) { & $Python -m venv .venv; Check-Exit }
$taskPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not $SkipInstall) {
    & $taskPython -m pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
    Check-Exit
    & $taskPython -m pip install -r requirements-validated.txt
    Check-Exit
    & $taskPython -m pip install -e '.[test,report]'
    Check-Exit
}
New-Item -ItemType Directory -Force external,.tools,data/models | Out-Null
$sources = @(
    @{ Name='villa'; Url='https://github.com/ScrollPrize/villa.git'; Ref='0e14cf48c8cee74b11e5e40a9d1d520b74e35423'; Paths=@('vesuvius') },
    @{ Name='volume-compressor'; Url='https://github.com/SuperOptimizer/volume-compressor.git'; Ref='20b03983ee741baa160d3e630da77a3b3a24ee44'; Paths=@('python','src') }
)
foreach ($source in $sources) {
    $target = 'external/' + $source.Name
    if (-not (Test-Path "$target/.git")) {
        git clone --filter=blob:none --depth 1 --sparse --no-checkout $source.Url $target; Check-Exit
        git -C $target sparse-checkout set @($source.Paths); Check-Exit
        git -C $target fetch --depth 1 origin $source.Ref; Check-Exit
        git -C $target checkout $source.Ref; Check-Exit
    }
    $head = git -C $target rev-parse HEAD; Check-Exit
    if ($head -ne $source.Ref) { throw "Upstream $target is not at the expected pin; no checkout is overwritten." }
}
if (-not (Test-Path '.tools/volcomp.dll')) {
    $archive = '.tools/llvm-mingw.zip'
    if (-not (Test-Path $archive)) {
        Invoke-WebRequest 'https://github.com/mstorsjo/llvm-mingw/releases/download/20260922/llvm-mingw-20260922-ucrt-x86_64.zip' -OutFile $archive
    }
    $digest = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower()
    if ($digest -ne 'e3ad77d117a4bea19a7a3b333341824d79a5a371004a10e25b8504e7b3047666') { throw 'Compiler archive checksum mismatch' }
    if (-not (Test-Path '.tools/llvm-mingw')) { Expand-Archive -LiteralPath $archive -DestinationPath '.tools/llvm-mingw' }
    $compiler = (Get-ChildItem '.tools/llvm-mingw' -Recurse -Filter 'clang.exe' | Select-Object -First 1).FullName
    & $compiler -std=c23 -O3 -shared -o .tools/volcomp.dll external/volume-compressor/python/volcomp_shim.c '-Wl,--export-all-symbols'
    Check-Exit
}
$modelHashes = @{ '42'='e635558ae6a1a807a7e5ec1e83adfd45bc3c0ac53883ea43f1d4e085d62a9cab'; '43'='2aeaa85a35ef28d7bc7bf3e848c4a6a91385e9132710927fdba41133c4ecb28f' }
foreach ($seed in @('42','43')) {
    $destination = "data/models/ink9-seed$seed.pth"
    if (-not (Test-Path $destination)) {
        Invoke-WebRequest "https://huggingface.co/scrollprize/ink_9um/resolve/7109667e2607db1b90c37c8b09cb876ea7fe7bb1/hybrid_3d2d-seed$seed/step-075000.pth" -OutFile "$destination.partial"
        Move-Item -LiteralPath "$destination.partial" -Destination $destination
    }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $modelHashes[$seed]) { throw "Model seed$seed checksum mismatch" }
}
& $taskPython -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
Check-Exit
