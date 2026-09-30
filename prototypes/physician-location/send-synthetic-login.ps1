# Synthetic test sender only. Does not inspect the current Windows user or device.
[CmdletBinding()]
param(
    [ValidateRange(1,25)][int]$Physician = 1,
    [ValidateSet('Office','Remote','Unknown','RemoteSession')][string]$Location = 'Office',
    [string]$BaseUrl = 'http://localhost:8002',
    [string]$Token = $env:PRESENCE_INGEST_TOKEN,
    [Guid]$EventId = [Guid]::NewGuid(),
    [DateTimeOffset]$OccurredAt = [DateTimeOffset]::UtcNow
)
$ErrorActionPreference = 'Stop'
$uri = [Uri]$BaseUrl
if ($uri.Host -notin @('localhost','127.0.0.1','[::1]')) { throw 'Synthetic sender only supports loopback destinations.' }
if (-not $Token) { throw 'Set PRESENCE_INGEST_TOKEN to the local prototype credential.' }
$roster = Invoke-RestMethod -Uri "$($BaseUrl.TrimEnd('/'))/work-location/physicians"
$id = 'synthetic-{0:d3}' -f $Physician
$person = $roster.physicians | Where-Object { $_.physician_id -eq $id }
$payload = @{
    event_id = $EventId.ToString(); physician_id = $id; username = $person.username
    occurred_at = $OccurredAt.ToUniversalTime().ToString('o'); event_type = 'logon'
    device_id = $(if ($Location -eq 'Remote') { 'DEMO-LAPTOP-01' } else { 'DEMO-MAIN-01' })
    session_type = $(if ($Location -eq 'RemoteSession') { 'remote' } else { 'console' })
    network_context = $(switch ($Location) { 'Remote' {'offsite'} 'Unknown' {'unknown'} default {'onsite'} })
    synthetic = $true
}
# For an exact replay, reuse both EventId and OccurredAt from the first call.
$body = $payload | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$($BaseUrl.TrimEnd('/'))/work-location/events" -Headers @{'X-Presence-Token'=$Token} -ContentType 'application/json' -Body $body
