import { Component } from '@angular/core';
import { SpecimenSourceService } from '../../../services/specimen-source.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';


@Component({
  standalone: false,
  selector: 'app-list-specimen-source',
  templateUrl: './list-specimen-source.component.html',
  styleUrls: ['./list-specimen-source.component.css']
})
export class ListSpecimenSourceComponent {
  specimenSources: any = [];
  
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;

  constructor(private specimenSourceService:SpecimenSourceService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
  });
    this.getAllSpecimenSources();
  }

  async getAllSpecimenSources(){
    const result = await this.specimenSourceService.getSpecimenSources(this.page,this.tableSize);
    if(result.status == true){
      this.specimenSources = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async deleteSpecimenSource(roleId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.specimenSourceService.deleteSpecimenSource(roleId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.getAllSpecimenSources();
        that.toastr.success('','Specimen source deleted successfully.');
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
    this.getAllSpecimenSources();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAllSpecimenSources();
  }
}
