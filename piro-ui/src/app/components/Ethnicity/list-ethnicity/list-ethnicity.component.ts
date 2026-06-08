import { Component } from '@angular/core';
import { EthnicityService } from '../../../services/ethnicity.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-list-ethnicity',
  templateUrl: './list-ethnicity.component.html',
  styleUrls: ['./list-ethnicity.component.css']
})
export class ListEthnicityComponent {
  items: any = [];
  
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;

  constructor(private ethnicityService:EthnicityService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    this.getAll();
  }

  async getAll(){
    const result = await this.ethnicityService.getAll(this.page,this.tableSize);
    if(result.status == true){
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async delete(roleId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.ethnicityService.delete(roleId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.getAll();
        that.toastr.success('','Ethnicity deleted successfully.');
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
    this.getAll();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAll();
  }
}
