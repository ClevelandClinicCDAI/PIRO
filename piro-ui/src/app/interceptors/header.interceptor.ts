import { Inject, Injectable, InjectionToken } from '@angular/core';
import { HttpInterceptor, HttpEvent, HttpRequest, HttpHandler, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, tap } from 'rxjs';
import { Router } from '@angular/router';
import { ToastService } from '../services/toast.service';
import { EventTypes } from '../models/event-types';
import { environment } from '../../environments/environment';
import { timeout } from 'rxjs/operators';
import { LocalStorageService } from '../services/localStorage.service';
import { SessionExpiryService } from '../services/session-expiry.service';
@Injectable()
export class HeaderInterceptor implements HttpInterceptor {
  constructor(private router: Router,
    private toastService: ToastService,
    private localStorageService: LocalStorageService,
    private sessionExpiry: SessionExpiryService) { }

  /**
   * True when `url` resolves under `environment.apiBaseUrl`, which may be
   * relative (`/api/`) or absolute (`https://api.example.com/`). Comparison is
   * segment-aware so `/apifoo` cannot match an `/api/` base.
   */
  private isApiRequest(url: string): boolean {
    try {
      const origin = window.location.origin;
      const requestUrl = new URL(url, origin);
      const apiBase = new URL(environment.apiBaseUrl || '/', origin);
      const basePath = apiBase.pathname.endsWith('/')
        ? apiBase.pathname
        : `${apiBase.pathname}/`;
      return requestUrl.origin === apiBase.origin &&
        `${requestUrl.pathname}/`.startsWith(basePath);
    } catch {
      return false;
    }
  }

  showoast(type: EventTypes, message: string, data: any) {
    switch (type) {
      case EventTypes.Success:
        this.toastService.showSuccessToast('Success', message, data);
        break;
      case EventTypes.Error:
        this.toastService.showErrorToast('Error', message, data);
        break;
      default:
        this.toastService.showInfoToast('Info', message, data);
        break;
    }
  }
  intercept(httpRequest: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // let ACCESS_TOKEN = localStorage.getItem('api-token');
    let ACCESS_TOKEN = this.localStorageService.getApiToken();
    var urlRequest = httpRequest.url.toLowerCase();
    var timeoutMsec = 300000;
    if (urlRequest.indexOf("/export") > 0) {
      timeoutMsec = 300000;
    } else if (urlRequest.indexOf("/cohort/create") > 0) {
      timeoutMsec = 300000;
    }
    // return next.handle(req).timeout(timeout);
    // Allowlist: attach the PIRO JWT only to requests under the configured API
    // base, so it can never reach the IdP or any other origin. A caller-supplied
    // Authorization header always wins.
    var isExcludeToken: Boolean = httpRequest.headers.has('Authorization') ||
      !this.isApiRequest(httpRequest.url) ||
      (urlRequest.indexOf("/login") > -1 || urlRequest.indexOf("/lastdataupdated") > -1);
    return next.handle((httpRequest.headers.get('Content-Type') == null && httpRequest.headers.get('ContentType') == null) ?
      httpRequest.clone(isExcludeToken ? {
        setHeaders:
          { 'Content-Type': 'application/json' }
      } :
        {
          setHeaders:
            { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + ACCESS_TOKEN }
        }) :
      httpRequest.clone(isExcludeToken ? {} :
        {
          setHeaders:
            { 'Authorization': 'Bearer ' + ACCESS_TOKEN }
        })).pipe(timeout(timeoutMsec)).pipe(tap((event: HttpEvent<any>) => {
          if (event instanceof HttpResponse) {
            // console.log(event.status)
            if (event.status == 200) {
              if (event.headers.has('Refreshtoken') && ACCESS_TOKEN === this.localStorageService.getApiToken()) {
                this.localStorageService.setApiToken(event.headers.get("Refreshtoken"));
              }
            }
          }
        },
          (err: any) => {
            if (err instanceof HttpErrorResponse) {
              console.log("Error: ", err);
              const isAuthCheck = urlRequest.indexOf('/token/isvalid') > -1 ||
                urlRequest.indexOf('/token/user') > -1;
              const isExpiredSignature = typeof err.error === 'string' &&
                /^Signature.*(failed|expired)/i.test(err.error);
              if (ACCESS_TOKEN && !isExcludeToken &&
                urlRequest.indexOf('/token/token') === -1 &&
                urlRequest.indexOf('/token/logout') === -1 &&
                (err.status === 401 || err.status === 403) &&
                (isAuthCheck || isExpiredSignature) &&
                this.sessionExpiry.expire(ACCESS_TOKEN)) {
                return;
              }
              const current = new Date();
              current.setMilliseconds(0);
              const timestamp: any = current.getTime();
              // const oldTimestamp: any = localStorage.getItem('lastErrorTimestamp');
              const oldTimestamp: any = this.localStorageService.getLastErrorTimestamp();
              let seconds = Math.abs(timestamp - oldTimestamp);
              if (seconds > 3000) {
                // if (err.status != 403 && err.status != 401) {
                //   this.showoast(EventTypes.Error, environment.errorExceptionMessage, []);
                // }

                if (err.status == 403 || err.status == 401) {
                  this.showoast(EventTypes.Error, environment.accessExceptionMessage, []);
                } else if (err.status == 510) {
                  // console.log(err);
                  if ((err?.error?.detail || '') != '') {
                    this.showoast(EventTypes.Error, err?.error?.detail, []);
                  } else if ((err?.error || '') != '') {
                    this.showoast(EventTypes.Error, err?.error, []);
                  } else {
                    this.showoast(EventTypes.Error, environment.errorExceptionMessage, []);
                  }
                } else {
                  // Suppress generic toast for endpoints that already handle errors in the component
                  const isHandledLocally =
                    urlRequest.indexOf('/extraction/preview') >= 0 ||
                    urlRequest.indexOf('/extraction/case/') >= 0;
                  if (!isHandledLocally) {
                    this.showoast(EventTypes.Error, environment.errorExceptionMessage, []);
                  }
                }
              }
              const current1 = new Date();
              current.setMilliseconds(0);
              const timestamp1: any = current.getTime();
              // localStorage.setItem('lastErrorTimestamp', timestamp1);
              this.localStorageService.setLastErrorTimestamp(timestamp1);
              //show toastr message
            }
          }));
  }
}