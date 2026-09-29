import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { FilterService } from './filter.service';
import { LocalStorageService } from './localStorage.service';

@Injectable({ providedIn: 'root' })
export class SessionExpiryService {
    constructor(
        private router: Router,
        private filterService: FilterService,
        private localStorageService: LocalStorageService
    ) { }

    expire(expectedToken?: string, returnUrl?: string): boolean {
        const token = this.localStorageService.getApiToken();
        if (!token || (expectedToken && token !== expectedToken)) {
            return false;
        }

        const destination = returnUrl || this.router.url;
        const isPublicPage = ['/login', '/signed-out', '/auth/callback'].some(
            path => destination === path || destination.startsWith(`${path}?`)
        );
        const safeReturnUrl = destination.startsWith('/') && destination !== '/'
            ? destination
            : '/search';

        this.localStorageService.clearItem('api-token');
        this.filterService.setLogin(false, '', true);
        if (!isPublicPage) {
            this.router.navigate(['/login'], {
                queryParams: { returnUrl: safeReturnUrl },
                replaceUrl: true,
            });
        }
        return true;
    }
}