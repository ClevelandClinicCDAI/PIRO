import { Component } from '@angular/core';
import { RaceService } from '../../../services/race.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

@Component({
  selector: 'app-list-race',
  templateUrl: './list-race.component.html',
  styleUrls: ['./list-race.component.css']
})
export class ListRaceComponent {
  items: any = [];
  
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;

  constructor(private raceService:RaceService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,private router: Router,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
  });
    this.getAll();
  }

  async getAll(){
    const result = await this.raceService.getAll(this.page,this.tableSize);
    if(result.status == true){
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
  }

  async delete(roleId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.raceService.delete(roleId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.getAll();
        that.toastr.success('','Race deleted successfully.');
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
