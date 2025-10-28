import { Component, Input  } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder  } from '@angular/forms';
import { environment } from '../../../../environments/environment';
import { ToastrService } from 'ngx-toastr';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { SavedSearchContentService } from '../../../services/saved-search-content.service';
import { LocalStorageService } from '../../../services/localStorage.service';

@Component({
  selector: 'app-savedsearchcontentmodal',
  templateUrl: './savedsearchcontentmodal.component.html',
  styleUrls: ['./savedsearchcontentmodal.component.css']
})
export class SavedsearchcontentmodalComponent {
  items: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;
  constructor(private activeModal: NgbActiveModal, 
    private savedSearchContentService:SavedSearchContentService,
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService,
    private localStorageService: LocalStorageService) {}

   async getAll(){
    const result = await this.savedSearchContentService.getContent(this.page,this.tableSize);
    if(result.status == true){
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
  }

  ngOnInit() {
    this.getAll();
  }

  async deleteSearch(searchId:number){
    let that = this;
    this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
      const result:any = await that.savedSearchContentService.deletContent(searchId);
      if(result.status == true){
        that.page = 1;
        that.count = 0;
        that.toastr.success('','Search deleted successfully.');
        that.getAll();
      }else{
        that.toastr.error('','Something went wrong.');
      }
    }, function () {  
      
    })  
  }
  
  closeModal() {
    this.activeModal.close('Modal Closed');
  }


  onTableDataChange(event: any) {
    this.page = event;
    this.getAll();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAll();
  }

  formatDateTime(date: any) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear(),
        hours = '' + d.getHours(),
        minutes = '' + d.getMinutes();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    if (hours.length < 2)
        hours = '0' + hours;
    if (minutes.length < 2)
        minutes = '0' + minutes;

    return [month,day, year].join('/') + " | " + hours + ":" + minutes;
  }

  assignAdvSearch(advSearch: any, mrn: any) {    
    this.localStorageService.setAdancedFilterData(JSON.parse(advSearch));
    this.localStorageService.setMrn(mrn);
  }
}
