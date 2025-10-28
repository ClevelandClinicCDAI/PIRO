import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, CanActivateFn, UrlTree, Route, UrlSegment, CanActivateChild, CanDeactivate, CanLoad } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable } from 'rxjs';
import { ToastService } from '../services/toast.service';
import { EventTypes } from '../models/event-types';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate, CanActivateChild, CanDeactivate<unknown>, CanLoad {
    constructor(
        private router: Router,
        private authService: AuthService,
        private toastService: ToastService
    ) {}
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
    // canActivate: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) =>  {
    //     const user = localStorage.getItem('api-token');
    //     if (user) {
    //         // authorised so return true
    //         return true;
    //     }

    //     // not logged in so redirect to login page with the return url
    //     this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
    //     return false;
    // }

    canActivate(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
        let url: string = state.url;
        return this.checkUserLogin(next, url,state);
      }
      canActivateChild(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
        return this.canActivate(next, state);
      }
      canDeactivate(
        component: unknown,
        currentRoute: ActivatedRouteSnapshot,
        currentState: RouterStateSnapshot,
        nextState?: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
        return true;
      }
      canLoad(
        route: Route,
        segments: UrlSegment[]): Observable<boolean> | Promise<boolean> | boolean {
        return true;
      }

      async checkUserLogin(route: ActivatedRouteSnapshot, url: any, state: RouterStateSnapshot): Promise<boolean> {
        // if (this.authService.getIsAuth()) {
        //   const userRole = this.authService.getRole();
        //   if (route.data['role']  &&  !route.data['role'].includes(userRole)) {
        //     this.showoast(EventTypes.Error, 'You do not have sufficient permission to access this.', []);
        //     this.router.navigate(['/home']);
        //     return false;
        //   }
        //   return true;
        // }

        const result:any = await this.authService.getIsAuth();
        if(result?.isauth){
          const userRole = result?.role;
          if (route.data['role']  &&  !route.data['role'].includes(userRole)) {
            this.showoast(EventTypes.Error, 'You do not have sufficient permission to access this.', []);
            this.router.navigate(['/home']);
            return false;
          }
          return true;
        }
        //this.router.navigate(['/home']);
        this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
        return false;
      }
}