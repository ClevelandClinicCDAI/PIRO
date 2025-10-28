import { Component } from '@angular/core';
import { AuditService } from '../../../services/audit.service'
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

@Component({
  selector: 'app-userhistory',
  templateUrl: './userhistory.component.html',
  styleUrls: ['./userhistory.component.css']
})
export class UserhistoryComponent {
  items: any = [];
  
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage * 2;

  constructor(private auditService:AuditService,
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService,
    private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
  });
    this.getAll();
  }

  async getAll(){
    const result = await this.auditService.getHistoryAll(this.page,this.tableSize);
    if(result.status == true){
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
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

  transform(input: string, inputAdv: string): string {    
    var searchRegExp = /##/g;
    var replaceWith = '<span class="form-item"><span class="bg-primary filteritem"><span class="filterDisplayName">';
    input = input.replace(searchRegExp, replaceWith);
    searchRegExp = /\$\$/g;
    replaceWith = '</span></span></span>';
    input = input.replace(searchRegExp, replaceWith);
    if ((inputAdv || '') != '') {
      input = input + '<span class="form-item"><span class="bg-primary filteritem advfilteritem"><span>' + 
      inputAdv + replaceWith;
    }
    return input;
  }
  
  openSearch(url: any) {
    // console.log(url);
    this.router.navigateByUrl(url);
  }
}