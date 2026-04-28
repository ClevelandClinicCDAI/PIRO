import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface AppConfig {
    apiBaseUrl: string;
    irbDisclaimerText: string;
}

@Injectable({
    providedIn: 'root'
})
export class AppConfigService {

    private config: AppConfig = { apiBaseUrl: '', irbDisclaimerText: '' };

    constructor(private http: HttpClient) { }

    loadConfig(): Promise<void> {
        return firstValueFrom(this.http.get<AppConfig>('assets/config.json'))
            .then(config => {
                this.config = config;
                environment.apiBaseUrl = config.apiBaseUrl;
            });
    }

    get apiBaseUrl(): string {
        return this.config.apiBaseUrl;
    }

    get irbDisclaimerText(): string {
        return this.config.irbDisclaimerText;
    }
}
