import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { LocalStorageService } from '../services/localStorage.service';
import { FilterService } from '../services/filter.service';
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authStatusListener = new Subject<boolean>();
  isAuthenticated: Boolean = false;
  roleAs: any = '';

  constructor(private http: HttpClient,
    private filterService:FilterService,
    private localStorageService: LocalStorageService) { }

  //Login User into system
  generateToken(username: any, password: any, islog: boolean) {
    let promise = new Promise((resolve, reject) => {
      let apiURL = environment.apiBaseUrl + 'token/token';
      // const body = {
      //   'query':'username='+username
      // };
      const body = {
        'username': username,
        'password': password,
        'islog': islog
      };
      this.http.post(apiURL, body)
        .subscribe({
          next: (res: any) => {
            resolve({ status: 200, body: res });
          },
          error: (err: any) => {
            resolve({ status: false, body: [] })
          },
          complete: () => {

          },
        });
    });
    return promise;
  }

  // getIsAuth() {
  //   // if(localStorage.getItem('api-token') !== null){
  //   if(this.localStorageService.getApiToken() !== null){
  //     return true;
  //   }else{
  //     return this.isAuthenticated;
  //   }
  // }

  getIsAuth() {

    let promise = new Promise((resolve, reject) => {
      if (this.localStorageService.getApiToken() == '') {
        resolve({ isauth: false, role: '' })
      } else {
        let apiURL = environment.apiBaseUrl + 'token/isvalid';
        this.http.get(apiURL)
          .subscribe({
            next: (res: any) => {
              resolve(res);
            },
            error: (err: any) => {
              resolve({ isauth: false, role: '' })
            },
            complete: () => {
            },
          });
      }
    });
    return promise;
  }


  getLastUpdateDate() {

    let promise = new Promise((resolve, reject) => {
      let apiURL = environment.apiBaseUrl + environment.lastdataupdatedUrl;
      this.http.get(apiURL)
        .subscribe({
          next: (res: any) => {
            resolve(res);
          },
          error: (err: any) => {
            resolve(undefined)
          },
          complete: () => {
          },
        });
    });
    return promise;
  }

  getUser() {

    let promise = new Promise((resolve, reject) => {
      if (this.localStorageService.getApiToken() == '') {
        resolve({ isauth: false, role: '' })
      } else {
        let apiURL = environment.apiBaseUrl + 'token/user';
        this.http.get(apiURL)
          .subscribe({
            next: (res: any) => {
              resolve(res);
            },
            error: (err: any) => {
              resolve({ isauth: false, name: '', nuid: '' })
            },
            complete: () => {
            },
          });
      }
    });
    return promise;
  }


  getAuthStatusListener() {
    return this.authStatusListener.asObservable();
  }

  parseJwt(token: any) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
  }


  async login(username: any, password: any, islog: boolean) {
    const result: any = await this.generateToken(username, password, islog);
    if (result.body?.access_token) {
      this.localStorageService.clear();
      this.localStorageService.setApiToken(result.body?.access_token);
      var userDetail = this.parseJwt(result.body?.access_token);
      this.isAuthenticated = true;
      this.roleAs = userDetail.role;
      // localStorage.setItem('role', this.roleAs);
      //this.localStorageService.setRole(this.roleAs);
      this.authStatusListener.next(true);
      return { 'status': true, 'message': 'Login Successful.', 'role': this.roleAs }
    } else {
      return { 'status': false, 'message': 'invalid.', 'role': '' }
    }
  }

  //Logout User from system
  logout() {
    // localStorage.removeItem('api-token');
    // localStorage.removeItem('searchFilter');
    // //localStorage.removeItem('produiuser');
    // localStorage.removeItem('role');
    this.localStorageService.clear();
    this.isAuthenticated = false;
    this.roleAs = '';
    this.filterService.setLogin(false, '', true);
    return { 'status': true, 'message': 'Login Successful.' }
  }


  // getRole() {
  //   this.roleAs = localStorage.getItem('role');
  //   return this.roleAs;
  // }

  getAttestation() {
    let promise = new Promise((resolve, reject) => {
      let apiURL = environment.apiBaseUrl + environment.getAttestationUrl;
      this.http.post(apiURL,{})
        .subscribe({
          next: (res: any) => {
            resolve(res);
          },
          error: (err: any) => {
            resolve(undefined)
          },
          complete: () => {
          },
        });
    });
    return promise;
  }

  saveAttestation() {
    let promise = new Promise((resolve, reject) => {
      let apiURL = environment.apiBaseUrl + environment.saveAttestationUrl;
      this.http.get(apiURL)
        .subscribe({
          next: (res: any) => {
            resolve(res);
          },
          error: (err: any) => {
            resolve(undefined)
          },
          complete: () => {
          },
        });
    });
    return promise;
  }
}
