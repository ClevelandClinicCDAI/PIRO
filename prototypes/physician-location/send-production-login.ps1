<#
.SYNOPSIS
    Sends a physician work-location login signal to the PIRO production API using
    an OAuth2 client-credentials JWT for authentication.

.DESCRIPTION
    1. Requests an access token from the OAuth2 token endpoint using the
       client_credentials grant.
    2. POSTs the login-event payload to PIRO's /work-location/events endpoint
       with "Authorization: Bearer <token>".

    Targets piro-api's POST /work-location/events, protected by a JWT issued
    from POST /token/service (client_credentials grant; see
    piro-api/backend/apis/version1/route_token.py and
    route_work_location.py). Unlike the prototype's X-Presence-Token shared
    secret, the token here is scoped via the WORK_LOCATION_INGEST role and
    expires after WORK_LOCATION_INGEST_TOKEN_EXPIRE_MINUTES.

.PARAMETER PhysicianId
    Identifier of the physician the signal belongs to.

.PARAMETER Username
    Physician's login/network username.

.PARAMETER DeviceId
    Identifier of the device/workstation that observed the login.

.PARAMETER OccurredAt
    Timezone-aware timestamp (ISO 8601) of when the login occurred.
    Defaults to "now" (UTC).

.PARAMETER BaseUrl
    Production PIRO API base URL. Defaults to $env:PIRO_BASE_URL or
    https://dev-piro.ccf.org.

.PARAMETER TokenUrl
    OAuth2 token endpoint (client_credentials grant). Defaults to
    $env:PIRO_TOKEN_URL, or "<BaseUrl>/token/service" (piro-api's own
    client_credentials endpoint) if unset.

.PARAMETER ClientId
    OAuth2 client id, matching WORK_LOCATION_INGEST_CLIENT_ID on the
    server. Defaults to $env:PIRO_CLIENT_ID.

.PARAMETER ClientSecret
    OAuth2 client secret, matching WORK_LOCATION_INGEST_CLIENT_SECRET on
    the server, as a SecureString. Defaults to $env:PIRO_CLIENT_SECRET
    converted to SecureString if set.

.PARAMETER Scope
    OAuth2 scope requested for the access token. Unused by piro-api's own
    /token/service endpoint (kept for compatibility with external IdPs).
    Defaults to $env:PIRO_SCOPE or "".

.EXAMPLE
    ./send-production-login.ps1 -PhysicianId 12345 -Username jdoe -DeviceId WS-100
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PhysicianId,

    [Parameter(Mandatory = $true)]
    [string]$Username,

    [Parameter(Mandatory = $true)]
    [string]$DeviceId,

    [string]$OccurredAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"),

    [string]$BaseUrl = $(if ($env:PIRO_BASE_URL) { $env:PIRO_BASE_URL } else { "https://dev-piro.ccf.org" }),

    [string]$TokenUrl = $env:PIRO_TOKEN_URL,

    [string]$ClientId = $env:PIRO_CLIENT_ID,

    [SecureString]$ClientSecret,

    [string]$Scope = $(if ($env:PIRO_SCOPE) { $env:PIRO_SCOPE } else { "" })
)

$ErrorActionPreference = "Stop"

if (-not $TokenUrl) { $TokenUrl = "$($BaseUrl.TrimEnd('/'))/token/service" }
if (-not $ClientId)  { throw "Set -ClientId or `$env:PIRO_CLIENT_ID." }

if (-not $ClientSecret) {
    if ($env:PIRO_CLIENT_SECRET) {
        $ClientSecret = ConvertTo-SecureString $env:PIRO_CLIENT_SECRET -AsPlainText -Force
    }
    else {
        throw "Provide -ClientSecret (SecureString) or set `$env:PIRO_CLIENT_SECRET."
    }
}

function Get-AccessToken {
    param(
        [string]$TokenUrl,
        [string]$ClientId,
        [SecureString]$ClientSecret,
        [string]$Scope
    )

    $plainSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientSecret))

    try {
        $body = @{
            grant_type    = "client_credentials"
            client_id     = $ClientId
            client_secret = $plainSecret
            scope         = $Scope
        }

        $response = Invoke-RestMethod -Method Post -Uri $TokenUrl -Body $body `
            -ContentType "application/x-www-form-urlencoded"

        return $response.access_token
    }
    finally {
        # Avoid keeping the plaintext secret in memory longer than necessary.
        $plainSecret = $null
    }
}

$eventId = [guid]::NewGuid().ToString()

$payload = @{
    event_id     = $eventId
    physician_id = $PhysicianId
    username     = $Username
    device_id    = $DeviceId
    occurred_at  = $OccurredAt
    synthetic    = $false
} | ConvertTo-Json -Compress

$accessToken = Get-AccessToken -TokenUrl $TokenUrl -ClientId $ClientId `
    -ClientSecret $ClientSecret -Scope $Scope

$headers = @{
    Authorization = "Bearer $accessToken"
}

$maxRetries = 3
$attempt    = 0
$delaySec   = 2

while ($true) {
    $attempt++
    try {
        $result = Invoke-RestMethod -Method Post `
            -Uri "$($BaseUrl.TrimEnd('/'))/work-location/events" `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $payload

        Write-Output "Sent event $eventId -> $($result | ConvertTo-Json -Compress)"
        break
    }
    catch {
        if ($attempt -ge $maxRetries) {
            throw "Failed to send event $eventId after $attempt attempts: $_"
        }
        Write-Warning "Attempt $attempt failed ($_). Retrying in $delaySec s..."
        Start-Sleep -Seconds $delaySec
        $delaySec *= 2
    }
}
