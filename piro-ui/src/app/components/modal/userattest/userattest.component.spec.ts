import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from '../../../services/auth.service';
import { UserattestComponent } from './userattest.component';

describe('UserattestComponent', () => {
  let component: UserattestComponent;
  let fixture: ComponentFixture<UserattestComponent>;
  let authService: AuthService;
  let router: Router;
  let saveAttestation: jasmine.Spy;
  let loginWithIdToken: jasmine.Spy;
  let login: jasmine.Spy;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserattestComponent]
    })
      .compileComponents();

    fixture = TestBed.createComponent(UserattestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    authService = TestBed.inject(AuthService);
    router = TestBed.inject(Router);
    saveAttestation = spyOn(authService, 'saveAttestation').and.resolveTo({});
    loginWithIdToken = spyOn(authService, 'loginWithIdToken').and.resolveTo({
      status: true,
      message: '',
      role: 'USER',
    });
    login = spyOn(authService, 'login').and.resolveTo({
      status: true,
      message: '',
      role: 'USER',
    });
    spyOn(router, 'navigateByUrl').and.resolveTo(true);
    spyOn(TestBed.inject(NgbActiveModal), 'close');
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('reissues the OAuth token after acceptance and returns to the saved url', async () => {
    component.idToken = 'id-token-value';
    component.returnUrl = '/search-detail/42';

    await component.attest('yes');

    expect(saveAttestation).toHaveBeenCalled();
    expect(loginWithIdToken).toHaveBeenCalledWith('id-token-value', true);
    expect(login).not.toHaveBeenCalled();
    expect(router.navigateByUrl).toHaveBeenCalledWith('/search-detail/42');
  });

  it('keeps using credentials and /search for the LDAP path', async () => {
    component.username = 'jdoe';
    component.password = 'secret';

    await component.attest('yes');

    expect(saveAttestation).toHaveBeenCalled();
    expect(login).toHaveBeenCalledWith('jdoe', 'secret', true);
    expect(loginWithIdToken).not.toHaveBeenCalled();
    expect(router.navigateByUrl).toHaveBeenCalledWith('/search');
  });

  it('does not record an attestation when the user declines', async () => {
    component.idToken = 'id-token-value';

    await component.attest('no');

    expect(saveAttestation).not.toHaveBeenCalled();
    expect(loginWithIdToken).toHaveBeenCalledWith('id-token-value', false);
  });
});
