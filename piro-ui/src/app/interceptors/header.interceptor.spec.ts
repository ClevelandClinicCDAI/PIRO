import { HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../environments/environment';
import { HeaderInterceptor } from './header.interceptor';

describe('HeaderInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  const originalApiBaseUrl = environment.apiBaseUrl;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        { provide: HTTP_INTERCEPTORS, useClass: HeaderInterceptor, multi: true },
      ],
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    localStorage.setItem('api-token', 'piro-jwt');
  });

  afterEach(() => {
    httpMock.verify();
    environment.apiBaseUrl = originalApiBaseUrl;
    localStorage.clear();
  });

  function authHeaderFor(url: string): string | null {
    http.get(url).subscribe({ next: () => { }, error: () => { } });
    const req = httpMock.expectOne(url);
    const header = req.request.headers.get('Authorization');
    req.flush({});
    return header;
  }

  it('attaches the token when apiBaseUrl is relative', () => {
    environment.apiBaseUrl = '/api/';

    expect(authHeaderFor('/api/token/isvalid')).toBe('Bearer piro-jwt');
  });

  it('attaches the token when apiBaseUrl is an absolute URL', () => {
    environment.apiBaseUrl = 'https://api.example.com:8082/';

    expect(authHeaderFor('https://api.example.com:8082/token/isvalid'))
      .toBe('Bearer piro-jwt');
  });

  it('never attaches the token to the IdP on another origin', () => {
    environment.apiBaseUrl = 'https://api.example.com:8082/';

    expect(authHeaderFor('https://login.example.com/tenant/oauth2/token'))
      .toBeNull();
  });

  it('never attaches the token to non-API same-origin requests', () => {
    environment.apiBaseUrl = '/api/';

    expect(authHeaderFor('assets/config.json')).toBeNull();
  });

  it('does not treat a lookalike path prefix as the API base', () => {
    environment.apiBaseUrl = '/api/';

    expect(authHeaderFor('/apifoo/token/isvalid')).toBeNull();
  });

  it('keeps the public endpoints unauthenticated', () => {
    environment.apiBaseUrl = '/api/';

    expect(authHeaderFor('/api/solr/lastdataupdated')).toBeNull();
  });
});
