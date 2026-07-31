import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FilterService } from '../../services/filter.service';
import { OidcService } from '../../services/oidc.service';
import { ToastService } from '../../services/toast.service';

/**
 * Landing page for the OIDC redirect URI (default `/auth/callback`).
 *
 * Exchanges the authorization code returned by the IdP for tokens,
 * then hands the id_token to the PIRO API's `/token/token` endpoint to
 * mint the internal PIRO JWT, and finally routes the user to their
 * intended destination.
 */
@Component({
    standalone: false,
    selector: 'app-auth-callback',
    template: `
    <div class="container text-center mt-5">
      <div *ngIf="!error">
        <div class="spinner-border" role="status" aria-hidden="true"></div>
        <p class="mt-3">Completing sign-in&hellip;</p>
      </div>
      <div *ngIf="error" class="alert alert-danger">
        <strong>Sign-in failed:</strong> {{ error }}
      </div>
    </div>
  `,
})
export class AuthCallbackComponent implements OnInit {
    error: string | null = null;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private authService: AuthService,
        private oidcService: OidcService,
        private filterService: FilterService,
        private toast: ToastService,
    ) { }

    async ngOnInit(): Promise<void> {
        const params = this.route.snapshot.queryParamMap;
        const code = params.get('code');
        const state = params.get('state');
        const oauthError = params.get('error');

        if (oauthError) {
            this.error = `${oauthError}: ${params.get('error_description') || ''}`;
            return;
        }
        if (!code || !state) {
            this.error = 'Missing code or state in callback.';
            return;
        }

        try {
            const idToken = await this.oidcService.handleCallback(code, state);
            const result = await this.authService.loginWithIdToken(idToken, true);
            if (!result.status) {
                this.error = result.message || 'PIRO rejected the id_token.';
                this.toast.showErrorToast('Error', this.error, []);
                return;
            }
            this.filterService.setLogin(true, result.role, true);
            const returnUrl = this.oidcService.consumeReturnUrl();
            this.router.navigateByUrl(returnUrl);
        } catch (err: any) {
            this.error = err?.message || String(err);
            this.toast.showErrorToast('Error', this.error!, []);
        }
    }
}
