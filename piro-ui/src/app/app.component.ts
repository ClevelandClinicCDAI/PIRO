import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';
import { FilterService } from './services/filter.service';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'PIRO';
  copyright = (new Date()).getFullYear();
  isAuthenticated: Boolean = false;
  lastUpdatedate: any = null;
  loginSubscription: any;

  constructor(private authService: AuthService,
    private filterService: FilterService,) {

  }

  async ngOnInit() {
    var auth: any = await this.authService.getUser();
    if(auth?.isauth) {
      this.authService.getLastUpdateDate().then((data: any) => {
        this.lastUpdatedate = data;
      });
    }

    this.loginSubscription = this.filterService.getLogin().subscribe((data: any) => {
      if (data.status) {
        if(data.isAuth) {
          this.authService.getLastUpdateDate().then((data: any) => {
            this.lastUpdatedate = data;
          });
        } else {
          this.lastUpdatedate = '';
        }
      }
    });
  }
}
