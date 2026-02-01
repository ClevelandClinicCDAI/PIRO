import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { ToastService } from '../../services/toast.service';
import { EventTypes } from '../../models/event-types';
import { LocalStorageService } from '../../services/localStorage.service';
import { FilterService } from '../../services/filter.service';
import {AivoteService} from '../../services/aivote.service';
import { ToastrService } from 'ngx-toastr';
@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  token: any = '';
  isAuthenticated: Boolean = false;
  role:string = '';
  isSearch:Boolean = false;
  isAdmin:Boolean = false;
  isRequestForm:Boolean = false;
  isRequestReview:Boolean = false;
  isMyHistory:Boolean = false;
  isAdminSecurity:Boolean = false;
  canRequestSlides:Boolean = false;
  canViewSlideQueue:Boolean = false;

  authListenerSubs: any;
  burgerChecked: boolean = false;
  loginSubscription:any;
  setIntervalId: any;
  constructor(private authService: AuthService,
    private voteService: AivoteService,
    private router: Router,
    private toastService: ToastService,
    private filterService:FilterService,
    private toastr: ToastrService,
    private localStorageService: LocalStorageService) {

  }

  async ngOnInit() {
    var auth: any = await this.authService.getIsAuth();
    this.isAuthenticated = auth?.isauth;
    this.role = auth?.role;
    // console.log("auth OnInit: ", auth);
    this.setSecurity();


    this.setIntervalId = setInterval(async () => {
      var auth: any = await this.authService.getIsAuth();
      if(!auth?.isauth) {
        this.logout();
      }
    }, 60000);

    this.loginSubscription = this.filterService.getLogin().subscribe((data: any) => {
      if (data.status) {
        this.isAuthenticated = data.isAuth;
        this.role = data.role;
        this.setSecurity();
        if(this.isAdmin) {
            this.voteService.isPending().then((data: any) => {
                if (data?.status && data?.data) {
                  this.toastr.success('', 'There are AI annotation review pending. Please go to "AI Annotation Feedback" page.');
                }
            });
        }
      }
    });
  }

  setSecurity() {
    // console.log("setSecurity");
    this.isSearch = ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER'].includes(this.role);
    this.isAdmin = ['ADMIN', 'DEMOADMIN'].includes(this.role);
    this.isRequestForm = ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER'].includes(this.role);
    this.isRequestReview = ['ADMIN', 'DEMOADMIN', 'ANALYST'].includes(this.role);
    this.isMyHistory = ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER'].includes(this.role);
    this.isAdminSecurity = ['SECURITYADMIN'].includes(this.role);
    this.canRequestSlides = ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER', 'SLIDEROOM'].includes(this.role);
    this.canViewSlideQueue = ['ADMIN', 'DEMOADMIN', 'SLIDEROOM'].includes(this.role);
    // console.log("this.isSearch", this.isSearch);
    // console.log("this.isAdmin", this.isAdmin);
    // console.log("this.isRequestForm", this.isRequestForm);
    // console.log("this.isRequestReview", this.isRequestReview);
    // console.log("this.isMyHistory", this.isMyHistory);
    // console.log("this.isAdminSecurity", this.isAdminSecurity);
  }

  logout() {
    this.burgerChecked = false;
    const resp = this.authService.logout();
    if (resp.status == true) {
      this.isAuthenticated = false;
      this.router.navigate(['/login']);
    }
  }
  ngOnDestroy() {
    this.authListenerSubs.unsubscribe();
    this.loginSubscription.unsubscribe();
    if (this.setIntervalId) {
      clearInterval(this.setIntervalId);
    }
  }

  changeBurger(event: any) {
    if (event.target.checked) {
      this.burgerChecked = true;
    } else {
      this.burgerChecked = false;
    }
  }
  triggerFun() {
    this.burgerChecked = false;
  }

  searchPage() {
    var searchUrlFrom: string = this.localStorageService.getSearchUrl();
    if (searchUrlFrom != '') {
      let params = searchUrlFrom.split('&page=');
      if (params.length > 0) {
        var searchFilter = params[0].replace('searchFilter=', '');
      } else {
        var searchFilter = '{}';
      }
      const arrSearchFilter = JSON.parse(searchFilter);
      if (!Array.isArray(arrSearchFilter)) {
        this.router.navigate(['/search']);
      } else {
        // console.log('arrSearchFilter', arrSearchFilter)
        var pagesortby = params[1].split('&sortBy=');
        var page = pagesortby[0];
        var sortBy = pagesortby[1];
        this.router.navigate(['/search'], {
          queryParams: { searchFilter: JSON.stringify(arrSearchFilter), page: page, sortBy: sortBy },
          replaceUrl: true
        });
      }
    } else {
      this.router.navigate(['/search']);
    }
  }
}
