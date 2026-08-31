import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { AppConfigService } from './app-config.service';

/**
 * Hand-rolled OpenID Connect client implementing the authorization-code
 * flow with PKCE (RFC 7636).
 *
 * Only used when `AppConfigService.authMode === 'OAUTH'`. Nothing here
 * runs when the API is configured for LDAP.
 *
 * We deliberately avoid adding `angular-oauth2-oidc` or `oidc-client-ts`
 * because the flow we need is small, the mock IdP contract is known,
 * and we want to keep the bundle size and dependency surface minimal.
 */
@Injectable({ providedIn: 'root' })
export class OidcService {
    private static readonly VERIFIER_KEY = 'pkce_verifier';
    private static readonly STATE_KEY = 'pkce_state';
    private static readonly RETURN_URL_KEY = 'pkce_return_url';

    constructor(
        private http: HttpClient,
        private appConfig: AppConfigService,
    ) { }

    /**
     * Redirect the browser to the IdP's authorization endpoint to begin
     * the code + PKCE flow. Persists the verifier and state in
     * sessionStorage so the callback can validate them.
     */
    async login(returnUrl: string = '/search'): Promise<void> {
        const verifier = this.randomUrlSafe(64);
        const challenge = await this.pkceChallenge(verifier);
        const state = this.randomUrlSafe(24);
        const authorizationEndpoint = await this.authorizationEndpoint();

        sessionStorage.setItem(OidcService.VERIFIER_KEY, verifier);
        sessionStorage.setItem(OidcService.STATE_KEY, state);
        sessionStorage.setItem(OidcService.RETURN_URL_KEY, returnUrl);

        const params = new URLSearchParams({
            response_type: 'code',
            client_id: this.appConfig.oidcClientId,
            redirect_uri: this.appConfig.oidcRedirectUri,
            scope: this.appConfig.oidcScopes,
            state,
            code_challenge: challenge,
            code_challenge_method: 'S256',
        });

        window.location.assign(`${authorizationEndpoint}?${params.toString()}`);
    }

    /**
     * Exchange an authorization code for tokens at the IdP's token
     * endpoint. Called from the callback route. Validates that the
     * returned `state` matches the value we stashed at login start.
     *
     * Returns the id_token so the caller can hand it off to the PIRO
     * API's `/token/token` endpoint.
     */
    async handleCallback(code: string, state: string): Promise<string> {
        const savedState = sessionStorage.getItem(OidcService.STATE_KEY);
        const verifier = sessionStorage.getItem(OidcService.VERIFIER_KEY);
        if (!savedState || savedState !== state) {
            throw new Error('OIDC state mismatch');
        }
        if (!verifier) {
            throw new Error('OIDC PKCE verifier missing');
        }

        // Discover the token endpoint to keep this decoupled from the IdP's
        // URL layout (mock-oauth uses `/token`, some IdPs use `/oauth2/token`).
        const tokenEndpoint = await this.tokenEndpoint();

        const body = new URLSearchParams();
        body.set('grant_type', 'authorization_code');
        body.set('code', code);
        body.set('redirect_uri', this.appConfig.oidcRedirectUri);
        body.set('client_id', this.appConfig.oidcClientId);
        body.set('code_verifier', verifier);

        const headers = new HttpHeaders({
            'Content-Type': 'application/x-www-form-urlencoded',
        });

        const response: any = await firstValueFrom(
            this.http.post(tokenEndpoint, body.toString(), { headers }),
        );

        // One-shot values; clear them so a page refresh can't replay.
        sessionStorage.removeItem(OidcService.STATE_KEY);
        sessionStorage.removeItem(OidcService.VERIFIER_KEY);

        if (!response?.id_token) {
            throw new Error('Token response missing id_token');
        }
        return response.id_token;
    }

    consumeReturnUrl(): string {
        const url = sessionStorage.getItem(OidcService.RETURN_URL_KEY) || '/search';
        sessionStorage.removeItem(OidcService.RETURN_URL_KEY);
        return url;
    }

    private async tokenEndpoint(): Promise<string> {
        const discovery = await this.discoveryDocument();
        if (!discovery?.token_endpoint) {
            throw new Error('OIDC discovery document missing token_endpoint');
        }
        return discovery.token_endpoint;
    }

    private async authorizationEndpoint(): Promise<string> {
        const discovery = await this.discoveryDocument();
        if (!discovery?.authorization_endpoint) {
            throw new Error('OIDC discovery document missing authorization_endpoint');
        }
        return discovery.authorization_endpoint;
    }

    private async discoveryDocument(): Promise<any> {
        const url =
            `${this.trimSlash(this.appConfig.oidcIssuer)}/.well-known/openid-configuration`;
        return firstValueFrom(this.http.get(url));
    }

    private trimSlash(url: string): string {
        return url.endsWith('/') ? url.slice(0, -1) : url;
    }

    private randomUrlSafe(byteLength: number): string {
        const bytes = new Uint8Array(byteLength);
        window.crypto.getRandomValues(bytes);
        return this.base64UrlEncode(bytes);
    }

    private async pkceChallenge(verifier: string): Promise<string> {
        const digest = await window.crypto.subtle.digest(
            'SHA-256',
            new TextEncoder().encode(verifier),
        );
        return this.base64UrlEncode(new Uint8Array(digest));
    }

    private base64UrlEncode(bytes: Uint8Array): string {
        let binary = '';
        for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window
            .btoa(binary)
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }
}
