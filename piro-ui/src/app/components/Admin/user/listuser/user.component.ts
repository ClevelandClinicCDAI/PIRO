import { Component } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../../environments/environment';
import { UserService } from '../../../../services/user.service';
import { ConfirmDialogService } from '../../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent {
  users: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;
  responsiveP: boolean = true;
  autoHideP: boolean = true;
  constructor(private userService: UserService, private toastr: ToastrService, private confirmDialogService: ConfirmDialogService, private router: Router,
    private activatedRoute: ActivatedRoute) { }
  ngOnInit() {
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    this.getAllUsers();
  }

  async getAllUsers() {
    const result = await this.userService.getUsers(this.page, this.tableSize);
    if (result.status == true) {
      this.users = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async deleteUser(userId: number) {
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {
      const result: any = await that.userService.deletUser(userId);
      if (result.status == true) {
        that.page = 1;
        that.count = 0;
        that.getAllUsers();
      } else {
        that.toastr.error('', 'Something went wrong.');
      }
    }, function () {

    });
  }

  onTableDataChange(event: any) {
    this.page = event;
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: { page: event },
      replaceUrl: true
    });
    this.getAllUsers();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAllUsers();
  }
}
