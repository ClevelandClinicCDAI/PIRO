import { Component } from '@angular/core';
import { SpecimenTypeService } from '../../../services/specimen-type.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';


@Component({
  standalone: false,
  selector: 'app-list-sepciment-type',
  templateUrl: './list-sepciment-type.component.html',
  styleUrls: ['./list-sepciment-type.component.css']
})
export class ListSepcimentTypeComponent {
  specimenTypes: any = [];
  
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;

  constructor(private specimenTypeService:SpecimenTypeService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    this.getAllSpecimenTypes();
  }

  async getAllSpecimenTypes(){
    const result = await this.specimenTypeService.getSpecimenTypes(this.page,this.tableSize);
    if(result.status == true){
      this.specimenTypes = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async deleteSpecimenType(roleId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.specimenTypeService.deleteSpecimenType(roleId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.getAllSpecimenTypes();
        that.toastr.success('','Specimen type deleted successfully.');
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
    this.getAllSpecimenTypes();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAllSpecimenTypes();
  }
}
