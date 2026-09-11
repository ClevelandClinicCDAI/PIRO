import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    service = TestBed.inject(AuthService);
    localStorage.clear();
  });

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
});
