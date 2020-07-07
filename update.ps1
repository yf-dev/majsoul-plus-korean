$resourcePackPath = '.\resourcepack.json'
$scriptName = 'update.ps1'
$scriptTempName = 'update.temp.ps1'
$scriptParentName = 'korean'

$global:progressPreference = 'silentlyContinue'

if ($MyInvocation.MyCommand.Name -eq $scriptName) {
    Write-Host '[.] Copy script to update.temp.ps1'
    Copy-Item ".\$scriptName" ".\$scriptTempName"
    Write-Host '[.] Run copied script'
    Start-Process powershell -ArgumentList ".\$scriptTempName"
    Exit
}
if ((Get-Item .).Name -ne $scriptParentName) {
    Write-Host '[!] This script is not placed properly: ' $MyInvocation.MyCommand.Path
    Remove-Item ".\$($scriptTempName)"
    Write-Host '[!] Update failed. Press enter key to exit.'
    [void][System.Console]::ReadKey($true)
    Exit
}
if (!(Test-Path $resourcePackPath -PathType Leaf)) {
    Write-Host '[!] Cannot found resourcePackPath: ' $resourcePackPath
    Remove-Item ".\$($scriptTempName)"
    Write-Host '[!] Update failed. Press enter key to exit.'
    [void][System.Console]::ReadKey($true)
    Exit
}
try {
    Write-Host '[-] Update the resource pack'

    $resourcePackJson = Get-Content $resourcePackPath -Encoding UTF8 | Out-String | ConvertFrom-Json
    Write-Host '[.] Current version: ' $resourcePackJson.version

    $releaseInfo = (Invoke-RestMethod -Method GET -Uri "https://api.github.com/repos/yf-dev/majsoul-plus-korean/releases/latest")
    $versionCode = $releaseInfo.tag_name
    $downloadUri = $releaseInfo.assets[0].browser_download_url

    Write-Host '[.] Latest version: ' $versionCode

    $confirmMsg = 'Do you want to update? [y/n]'
    $confirm = Read-Host $confirmMsg
    while ($confirm -ne 'y') {
        if ($confirm -eq 'n') { exit }
        $confirm = Read-Host $confirmMsg
    }

    Write-Host '[.] Downloading the resource pack...'
    $pathZip = Join-Path -Path $([System.IO.Path]::GetTempPath()) -ChildPath ($(Split-Path -Path $downloadUri -Leaf) + '.zip')
    Invoke-WebRequest -Uri $downloadUri -Out $pathZip 

    Write-Host '[.] Extracting the resource pack...'
    $tempExtract = Join-Path -Path $([System.IO.Path]::GetTempPath()) -ChildPath $((New-Guid).Guid)
    Expand-Archive -Path $pathZip -DestinationPath $tempExtract -Force

    Write-Host '[.] Remove old resource pack data...'
    Get-ChildItem -Path '.\' -Exclude ".\$scriptTempName" | Remove-Item -Recurse -Force

    Write-Host '[.] Copy new resource pack data...'
    Move-Item -Path "$tempExtract\korean\*" -Destination '.\' -Force

    Write-Host '[.] Clean temporary data...'
    Remove-Item -Path $tempExtract -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item $pathZip -Force

    Write-Host '[-] Update Completed. Press enter key to exit.'
    [void][System.Console]::ReadKey($true)
}
catch {
    Write-Host $_
    Write-Host '[!] Update failed. Press enter key to exit.'
    [void][System.Console]::ReadKey($true)
}
finally {
    Remove-Item ".\$($scriptTempName)"
}