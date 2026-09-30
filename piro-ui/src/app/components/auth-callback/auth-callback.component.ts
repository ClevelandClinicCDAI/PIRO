import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from '../../services/auth.service';
import { FilterService } from '../../services/filter.service';
import { OidcService } from '../../services/oidc.service';
import { ToastService } from '../../services/toast.service';
import { UserattestComponent } from '../modal/userattest/userattest.component';

/**
 * Landing page for the OIDC redirect URI (default `/auth/callback`).
 *
 * Exchanges the authorization code returned by the IdP for tokens,
 * then hands the id_token to the PIRO API's `/token/token` endpoint to
 * mint the internal PIRO JWT, applies the same attestation gate as the
 * LDAP sign-in path, and finally routes the user to their intended
 * destination.
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
        private modalService: NgbModal,
    ) { }

    async ngOnInit(): Promise<void> {
        const params = this.route.snapshot.queryParamMap;
        const code = params.get('code');
        const state = params.get('state');
        const oauthError = params.get('error');

        if (oauthError) {
            this.error = `${oauthError}: ${params.get('error_description') || ''}`;
            this.returnToLoginWithError(this.error ?? 'Sign-in failed.');
            return;
        }
        if (!code || !state) {
            this.error = 'Missing code or state in callback.';
            this.returnToLoginWithError(this.error ?? 'Sign-in failed.');
            return;
        }

        try {
            const idToken = await this.oidcService.handleCallback(code, state);
            const result = await this.authService.loginWithIdToken(idToken, true);
            if (!result.status) {
                this.error = result.message || 'PIRO rejected the id_token.';
                this.returnToLoginWithError(this.error ?? 'Sign-in failed.');
                return;
            }
            const returnUrl = this.oidcService.consumeReturnUrl();
            if (await this.promptForAttestation(idToken, result.role, returnUrl)) {
                return;
            }
            this.filterService.setLogin(true, result.role, true);
            this.router.navigateByUrl(returnUrl);
        } catch (err: any) {
            this.error = err?.message || String(err);
            this.returnToLoginWithError(this.error ?? 'Sign-in failed.');
        }
    }

    private returnToLoginWithError(
        message: string | null,
        returnUrl?: string,
    ): void {
        const safeMessage = message || 'Sign-in failed.';
        this.toast.showErrorToast('Error', safeMessage, []);
        this.router.navigate(['/login'], {
            queryParams: {
                oauthError: '1',
                returnUrl: returnUrl ?? this.oidcService.consumeReturnUrl(),
            },
            replaceUrl: true,
        });
    }

    /**
     * Mirrors the LDAP sign-in gate: an un-attested user must accept the
     * attestation before the session is usable. Returns true when the
     * modal has taken ownership of the post-login navigation.
     */
    private async promptForAttestation(
        idToken: string,
        role: string,
        returnUrl: string,
    ): Promise<boolean> {
        const attestation: any = await this.authService.getAttestation();
        if (!attestation) {
            // Never leave the user holding an un-attested session.
            this.authService.logout();
            this.error = 'Unable to confirm the attestation requirement.';
            this.returnToLoginWithError(this.error, returnUrl);
            return true;
        }
        if (!attestation.enabled || attestation.isAttest) {
            return false;
        }

        const modalRef = this.modalService.open(UserattestComponent, {
            ariaLabelledBy: 'modal-basic-title',
            size: 'lg',
            scrollable: true,
            backdrop: 'static',
            keyboard: false,
        });
        modalRef.componentInstance.isAuth = true;
        modalRef.componentInstance.role = role;
        modalRef.componentInstance.status = true;
        modalRef.componentInstance.textAttest = attestation.textAttest;
        modalRef.componentInstance.requireAttest = attestation.requireAttest;
        modalRef.componentInstance.idToken = idToken;
        modalRef.componentInstance.returnUrl = returnUrl;

        modalRef.result.catch((err: any) => {
            if (err != 1) {
                this.toast.showErrorToast('Error', 'Something went wrong.', []);
            }
        });
        return true;
    }
}
