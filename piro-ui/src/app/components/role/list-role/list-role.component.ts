import { Component } from '@angular/core';
import { RoleService } from '../../../services/role.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
@Component({
  standalone: false,
  selector: 'app-list-role',
  templateUrl: './list-role.component.html',
  styleUrls: ['./list-role.component.css']
})
export class ListRoleComponent {
  roles: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;

  constructor(private roleService:RoleService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    this.getAllRoles();
  }

  async getAllRoles(){
    // let page:number = 1;
    // let size:number = 10;
    const result = await this.roleService.getRoles(this.page,this.tableSize);
    if(result.status == true){
      this.roles = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async deleteRole(roleId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.roleService.deleteRole(roleId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.getAllRoles();
        that.toastr.success('','Role deleted successfully.');
      }else{
        that.toastr.error('','Something went wrong.');
      }
    }, function () {  
      
    })  
    
  }

  onTableDataChange(event: any) {
    this.page = event;
    this.router.navigate([], { 
      relativeTo: this.activatedRoute, 
      queryParams: {  page: event  },
      replaceUrl: true
    });
    this.getAllRoles();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAllRoles();
  }
}
