import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { fakeAsync, TestBed, tick } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { environment } from 'src/environments/environment';
import { AuthService } from './auth.service';

@Component({ template: '', standalone: false })
class TestPageComponent { }

describe('AuthService', () => {
  let service: AuthService;
  let router: Router;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, RouterTestingModule.withRoutes([
        { path: 'search-detail/:id', component: TestPageComponent },
        { path: 'search', component: TestPageComponent },
        { path: 'login', component: TestPageComponent },
      ])],
      declarations: [TestPageComponent],
    });
    service = TestBed.inject(AuthService);
    router = TestBed.inject(Router);
    httpMock = TestBed.inject(HttpTestingController);
    localStorage.clear();
  });

  afterEach(() => httpMock.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should detect expired stored JWTs and clear them', () => {
    const expiredToken = 'eyJhbGciOiJub25lIn0.eyJleHAiOjE3MDAwMDAwMDB9.';
    localStorage.setItem('api-token', expiredToken);

    expect(service.isTokenExpired(expiredToken)).toBeTrue();
    expect(service.clearExpiredSessionIfNeeded()).toBeTrue();
    expect(localStorage.getItem('api-token')).toBeNull();
  });

  it('should not clear valid stored JWTs', () => {
    const future = Math.floor((Date.now() + 3600000) / 1000);
    const validToken = `eyJhbGciOiJub25lIn0.${btoa(JSON.stringify({ exp: future }))}.signature`;
    localStorage.setItem('api-token', validToken);

    expect(service.isTokenExpired(validToken)).toBeFalse();
    expect(service.clearExpiredSessionIfNeeded()).toBeFalse();
    expect(localStorage.getItem('api-token')).toBe(validToken);
  });

  it('returns to the current protected URL on expiry without starting another redirect', fakeAsync(() => {
    router.navigateByUrl('/search-detail/42?tab=notes');
    tick();
    localStorage.setItem('api-token', 'eyJhbGciOiJub25lIn0.eyJleHAiOjE3MDAwMDAwMDB9.');

    expect(service.clearExpiredSessionIfNeeded()).toBeTrue();
    tick();
    expect(router.url).toBe('/login?returnUrl=%2Fsearch-detail%2F42%3Ftab%3Dnotes');
    expect(localStorage.getItem('api-token')).toBeNull();
    expect(service.clearExpiredSessionIfNeeded()).toBeFalse();
    expect(router.url).toBe('/login?returnUrl=%2Fsearch-detail%2F42%3Ftab%3Dnotes');
  }));

  it('falls back to search when expiry occurs without a protected route', fakeAsync(() => {
    localStorage.setItem('api-token', 'eyJhbGciOiJub25lIn0.eyJleHAiOjE3MDAwMDAwMDB9.');

    expect(service.clearExpiredSessionIfNeeded()).toBeTrue();
    tick();
    expect(router.url).toBe('/login?returnUrl=%2Fsearch');
  }));

  it('reauthenticates on a rejected PIRO validity check, but not on server failure', fakeAsync(() => {
    router.navigateByUrl('/search');
    tick();
    const future = Math.floor((Date.now() + 3600000) / 1000);
    const token = `eyJhbGciOiJub25lIn0.${btoa(JSON.stringify({ exp: future }))}.signature`;
    localStorage.setItem('api-token', token);

    service.getIsAuth();
    httpMock.expectOne(`${environment.apiBaseUrl}token/isvalid`).flush('Server error', {
      status: 500, statusText: 'Server Error'
    });
    tick();
    expect(router.url).toBe('/search');
    expect(localStorage.getItem('api-token')).toBe(token);

    service.getIsAuth();
    httpMock.expectOne(`${environment.apiBaseUrl}token/isvalid`).flush('Invalid token', {
      status: 403, statusText: 'Forbidden'
    });
    tick();
    expect(router.url).toBe('/login?returnUrl=%2Fsearch');
    expect(localStorage.getItem('api-token')).toBeNull();
  }));
});
