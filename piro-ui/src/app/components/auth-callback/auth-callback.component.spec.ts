import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from '../../services/auth.service';
import { OidcService } from '../../services/oidc.service';
import { AuthCallbackComponent } from './auth-callback.component';
import { UserattestComponent } from '../modal/userattest/userattest.component';

describe('AuthCallbackComponent', () => {
    let fixture: ComponentFixture<AuthCallbackComponent>;
    let router: Router;
    let authService: AuthService;
    let oidcService: OidcService;
    let modalService: NgbModal;
    let modalRef: { componentInstance: any; result: Promise<any> };

    function configure(queryParams: Record<string, string>) {
        TestBed.configureTestingModule({
            declarations: [AuthCallbackComponent],
            providers: [
                {
                    provide: ActivatedRoute,
                    useValue: {
                        snapshot: { queryParamMap: convertToParamMap(queryParams) },
                    },
                },
            ],
        });

        fixture = TestBed.createComponent(AuthCallbackComponent);
        router = TestBed.inject(Router);
        authService = TestBed.inject(AuthService);
        oidcService = TestBed.inject(OidcService);
        modalService = TestBed.inject(NgbModal);

        modalRef = { componentInstance: {}, result: Promise.resolve('closed') };
        spyOn(modalService, 'open').and.returnValue(modalRef as any);
        spyOn(router, 'navigateByUrl').and.resolveTo(true);
        spyOn(router, 'navigate').and.resolveTo(true);
        spyOn(oidcService, 'handleCallback').and.resolveTo('id-token-value');
        spyOn(oidcService, 'consumeReturnUrl').and.returnValue('/search-detail/42');
        spyOn(authService, 'loginWithIdToken').and.resolveTo({
            status: true,
            message: 'Login Successful.',
            role: 'USER',
        });
    }

    it('blocks access and prompts when attestation is required', async () => {
        configure({ code: 'abc', state: 'xyz' });
        spyOn(authService, 'getAttestation').and.resolveTo({
            enabled: true,
            isAttest: false,
            requireAttest: true,
            textAttest: 'Please attest.',
        });

        await fixture.componentInstance.ngOnInit();

        expect(modalService.open).toHaveBeenCalledWith(
            UserattestComponent,
            jasmine.objectContaining({ backdrop: 'static', keyboard: false })
        );
        expect(modalRef.componentInstance.idToken).toBe('id-token-value');
        expect(modalRef.componentInstance.returnUrl).toBe('/search-detail/42');
        expect(modalRef.componentInstance.requireAttest).toBeTrue();
        expect(router.navigateByUrl).not.toHaveBeenCalled();
    });

    it('proceeds without prompting when the user has already attested', async () => {
        configure({ code: 'abc', state: 'xyz' });
        spyOn(authService, 'getAttestation').and.resolveTo({
            enabled: true,
            isAttest: true,
            requireAttest: true,
            textAttest: 'Please attest.',
        });

        await fixture.componentInstance.ngOnInit();

        expect(modalService.open).not.toHaveBeenCalled();
        expect(router.navigateByUrl).toHaveBeenCalledWith('/search-detail/42');
    });

    it('proceeds without prompting when attestation is disabled', async () => {
        configure({ code: 'abc', state: 'xyz' });
        spyOn(authService, 'getAttestation').and.resolveTo({
            enabled: false,
            isAttest: false,
            requireAttest: false,
            textAttest: '',
        });

        await fixture.componentInstance.ngOnInit();

        expect(modalService.open).not.toHaveBeenCalled();
        expect(router.navigateByUrl).toHaveBeenCalledWith('/search-detail/42');
    });

    it('clears the session when attestation status cannot be determined', async () => {
        configure({ code: 'abc', state: 'xyz' });
        spyOn(authService, 'getAttestation').and.resolveTo(undefined);
        const logout = spyOn(authService, 'logout').and.returnValue({
            status: true,
            message: '',
        });

        await fixture.componentInstance.ngOnInit();

        expect(logout).toHaveBeenCalled();
        expect(modalService.open).not.toHaveBeenCalled();
        expect(router.navigateByUrl).not.toHaveBeenCalled();
        expect(router.navigate).toHaveBeenCalledWith(
            ['/login'],
            jasmine.objectContaining({
                queryParams: jasmine.objectContaining({ oauthError: '1' }),
            })
        );
    });
});
