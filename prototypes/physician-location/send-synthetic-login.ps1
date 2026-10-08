# Synthetic test sender only. Does not inspect the current Windows user or device.
[CmdletBinding()]
param(
    [ValidateRange(1,2147483647)][int]$Physician = 1,
    [ValidateSet('Office','Remote','Unknown','RemoteSession')][string]$Location = 'Office',
    [string]$BaseUrl = 'http://localhost:8002',
    [string]$Token = $env:PRESENCE_INGEST_TOKEN,
    [Guid]$EventId = [Guid]::NewGuid(),
    [DateTimeOffset]$OccurredAt = [DateTimeOffset]::UtcNow,
    [string]$Building = ''
)
$ErrorActionPreference = 'Stop'
$uri = [Uri]$BaseUrl
if ($uri.Host -notin @('localhost','127.0.0.1','[::1]')) { throw 'Synthetic sender only supports loopback destinations.' }
if (-not $Token) { throw 'Set PRESENCE_INGEST_TOKEN to the local prototype credential.' }
$devices = (Get-Content -Raw (Join-Path $PSScriptRoot 'buildings.json') | ConvertFrom-Json).PSObject.Properties
$deviceIds = @($devices.Name)
$deviceId = $deviceIds[($Physician - 1) % $deviceIds.Count]
if ($Building) {
    if ($Location -ne 'Office') { throw '-Building requires -Location Office.' }
    $match = $devices | Where-Object { $_.Value -eq $Building }
    if (-not $match) { throw "Unknown building. Choose one of: $($devices.Value -join ', ')" }
    $deviceId = $match.Name
}
$roster = Invoke-RestMethod -Uri "$($BaseUrl.TrimEnd('/'))/work-location/physicians"
if ($Physician -gt $roster.physicians.Count) { throw "Physician must be between 1 and $($roster.physicians.Count)." }
$person = $roster.physicians[$Physician - 1]
$id = $person.physician_id
$payload = @{
    event_id = $EventId.ToString(); physician_id = $id; username = $person.username
    occurred_at = $OccurredAt.ToUniversalTime().ToString('o'); event_type = 'logon'
    device_id = $(if ($Location -eq 'Remote') { 'DEMO-LAPTOP-01' } else { $deviceId })
    session_type = $(if ($Location -eq 'RemoteSession') { 'remote' } else { 'console' })
    network_context = $(switch ($Location) { 'Remote' {'offsite'} 'Unknown' {'unknown'} default {'onsite'} })
    synthetic = $true
}
# For an exact replay, reuse both EventId and OccurredAt from the first call.
$body = $payload | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$($BaseUrl.TrimEnd('/'))/work-location/events" -Headers @{'X-Presence-Token'=$Token} -ContentType 'application/json' -Body $body
