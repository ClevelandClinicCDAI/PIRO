import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface AppConfig {
    apiBaseUrl: string;
    irbDisclaimerText: string;
    /**
     * Authentication mode. Set at container startup from the `AUTH_MODE`
     * env var. "LDAP" (default) keeps the existing username/password
     * form; "OAUTH" routes users through the IdP's browser-based flow.
     */
    authMode?: string;
    oidcIssuer?: string;
    oidcClientId?: string;
    oidcRedirectUri?: string;
    oidcScopes?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AppConfigService {

    private config: AppConfig = {
        apiBaseUrl: '',
        irbDisclaimerText: '',
        authMode: 'LDAP',
        oidcIssuer: '',
        oidcClientId: '',
        oidcRedirectUri: '',
        oidcScopes: 'openid profile email',
    };

    constructor(private http: HttpClient) { }

    loadConfig(): Promise<void> {
        return firstValueFrom(this.http.get<AppConfig>('assets/config.json'))
            .then(config => {
                this.config = { ...this.config, ...config };
                environment.apiBaseUrl = this.config.apiBaseUrl;
            });
    }

    get apiBaseUrl(): string {
        return this.config.apiBaseUrl;
    }

    get irbDisclaimerText(): string {
        return this.config.irbDisclaimerText;
    }

    get authMode(): string {
        return (this.config.authMode || 'LDAP').toUpperCase();
    }

    get isOAuthMode(): boolean {
        return this.authMode === 'OAUTH';
    }

    get oidcIssuer(): string {
        return this.config.oidcIssuer || '';
    }

    get oidcClientId(): string {
        return this.config.oidcClientId || '';
    }

    get oidcRedirectUri(): string {
        return this.config.oidcRedirectUri || '';
    }

    get oidcScopes(): string {
        return this.config.oidcScopes || 'openid profile email';
    }
}
