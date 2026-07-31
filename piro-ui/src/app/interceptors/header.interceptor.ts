import { Inject, Injectable, InjectionToken } from '@angular/core';
import { HttpInterceptor, HttpEvent, HttpRequest, HttpHandler, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, tap } from 'rxjs';
import { Router } from '@angular/router';
import { ToastService } from '../services/toast.service';
import { EventTypes } from '../models/event-types';
import { environment } from '../../environments/environment';
import { timeout } from 'rxjs/operators';
import { LocalStorageService } from '../services/localStorage.service';
@Injectable()
export class HeaderInterceptor implements HttpInterceptor {
  constructor(private router: Router,
    private toastService: ToastService,
    private localStorageService: LocalStorageService) { }
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
    // Absolute URLs are cross-origin (e.g. OIDC discovery + token endpoint on the
    // IdP). Never attach the PIRO JWT to those — the IdP shouldn't receive it,
    // and it would also leak the token to a foreign origin.
    var isAbsoluteUrl: boolean = /^https?:\/\//i.test(urlRequest);
    var isExcludeToken: Boolean = isAbsoluteUrl || (urlRequest.indexOf("/login") > -1 || urlRequest.indexOf("/lastdataupdated") > -1);
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
              if (event.headers.has('Refreshtoken')) {
                this.localStorageService.setApiToken(event.headers.get("Refreshtoken"));
              }
            }
          }
        },
          (err: any) => {
            if (err instanceof HttpErrorResponse) {
              console.log("Error: ", err);
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

                if (urlRequest.indexOf("/token") > 0) {
                  localStorage.removeItem('api-token')
                  this.router.navigate(['login']);
                } else if (err.status == 403 || err.status == 401) {
                  var re = new RegExp("^Signature.*(failed|expired)+.*$");
                  if (re.test(err.error)) {
                    this.router.navigate(['login']);
                    return;
                  }
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
                  this.showoast(EventTypes.Error, environment.errorExceptionMessage, []);
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