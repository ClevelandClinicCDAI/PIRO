import { Component } from '@angular/core';
import { RequesthistoryService } from '../../services/requesthistory.service';
import { ToastrService } from 'ngx-toastr';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { environment } from '../../../environments/environment';
import { ConfirmDialogService } from '../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { Common } from '../../helpers';
import { HttpResponse } from '@angular/common/http';
import { ViewsearchComponent } from '../modal/viewsearch/viewsearch.component';
import { ExportfieldComponent } from '../modal/exportfield/exportfield.component';
import { RequestNotesComponent } from '../modal/request-notes/request-notes.component';
@Component({
  standalone: false,
  selector: 'app-requesthistory',
  templateUrl: './requesthistory.component.html',
  styleUrls: ['./requesthistory.component.css']
})
export class RequesthistoryComponent {
  items: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;
  tcommon: Common;
  excelUrl: string = environment.apiBaseUrl + 'searchrequest/export/';
  contentLoaded = true;
  filterSelect: string = "0";
  contentText: string = "";
  isSubmit: boolean = true;
  isApproved: boolean = false;
  isDenied: boolean = false;
  isClosed: boolean = false;
  recordStatus: string = 'SUBMIT';
  constructor(private requesthistoryService: RequesthistoryService,
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService,
    private router: Router,
    private modalService: NgbModal,
    private activatedRoute: ActivatedRoute,
    private common: Common) {
    this.tcommon = common
  }
  ngOnInit() {
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    // this.getMy();
    this.filterData(true);
  }

  async ondelete(searchRequestId: number) {
    let that = this;
    this.confirmDialogService.confirmThis('Are you sure to delete the request?', async function () {
      that.contentLoaded = false;
      const result = await that.requesthistoryService.delete(searchRequestId);
      that.contentLoaded = true;
      if (result.status == true) {
        that.filterData(true);
      }
    }, function () {
      that.contentLoaded = true;
    });
  }

  async onapprove(searchRequestId: number) {
    let that = this;
    this.confirmDialogService.confirmThis('Are you sure to approve the request?', async function () {
      that.contentLoaded = false;
      const result = await that.requesthistoryService.approve(searchRequestId);
      that.contentLoaded = true;
      if (result.status == true) {
        that.filterData(true);
      }
    }, function () {
      that.contentLoaded = true;
    });
  }

  async ondeny(searchRequestId: number) {
    let that = this;
    this.confirmDialogService.confirmThis('Are you sure to deny the request?', async function () {
      that.contentLoaded = false;
      const result = await that.requesthistoryService.deny(searchRequestId);
      that.contentLoaded = true;
      if (result.status == true) {
        that.filterData(true);
      }
    }, function () {
      that.contentLoaded = true;
    });
  }

  async onclose(searchRequestId: number) {
    let that = this;
    this.confirmDialogService.confirmThis('Are you sure to close the request?', async function () {
      that.contentLoaded = false;
      const result = await that.requesthistoryService.close(searchRequestId);
      that.contentLoaded = true;
      if (result.status == true) {        
        that.filterData(true);
      }
    }, function () {
      that.contentLoaded = true;
    });
  }

  async filterData(pagereset: boolean) {
    this.contentLoaded = false;
    if(pagereset) {
      this.page = 1;
    }    
    const result = await this.requesthistoryService.getAllStatus(this.recordStatus, this.page, this.tableSize);
    if (result.status == true) {
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
    this.contentLoaded = true;
  }
  onTableDataChange(event: any) {
    this.page = event;
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: { page: event },
      replaceUrl: true
    });
    this.filterData(false);
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.filterData(false);
  }


  async viewsearch(searchId: number) {
    const modalRef = this.modalService.open(ViewsearchComponent, 
      { ariaLabelledBy: 'modal-basic-title', size: 'xl', scrollable: true });
    modalRef.componentInstance.SearchId = searchId;
		modalRef.result.then((result) => {

		}).catch((error) => {

		});
  }

  
  async filedownload(searchRequestId: number, extn: string) {
    this.contentLoaded = false;
    this.contentText = "Downloading the IRB file...";
    this.requesthistoryService.getFile(searchRequestId).subscribe(async (event) => {
      let data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });
      if (downloadedFile.type != "") {
        const a = document.createElement('a');
        a.setAttribute('style', 'display:none;');
        document.body.appendChild(a);
        a.download = `IRB_${searchRequestId}${extn}`;
        a.href = URL.createObjectURL(downloadedFile);
        a.target = '_blank';
        this.contentLoaded = true;
        a.click();
        document.body.removeChild(a);
      }
    },
      error => {
        this.contentLoaded = true;
      });
  }

  async onexcel(searchRequestId: number) {
    this.contentLoaded = false;
    this.contentText = "Downloading the report...";
    this.requesthistoryService.getExport(searchRequestId).subscribe(async (event) => {
      let data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });
      if (downloadedFile.type != "") {
        const a = document.createElement('a');
        a.setAttribute('style', 'display:none;');
        document.body.appendChild(a);
        var newDate = new Date();
        var datetime = new Date().toLocaleString().replace(',', '');
        a.download = "piroExport_" + datetime + ".xlsx"
        a.href = URL.createObjectURL(downloadedFile);
        a.target = '_blank';
        this.contentLoaded = true;
        a.click();
        document.body.removeChild(a);
      }
    },
      error => {
        this.contentLoaded = true;
      });
  }

  openexportfieldModal(searchRequestId: number) {
		const modalRef = this.modalService.open(ExportfieldComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
    if(this.isSubmit) {
      modalRef.componentInstance.isUpdate = true;
    } else 
    {
      modalRef.componentInstance.isReadonly = true;
    }
    
    modalRef.componentInstance.searchRequestId = searchRequestId;
		modalRef.result.then((result) => {
      // console.log(result);
      if(result.length > 0) {
        // this.selectedFields = result;
        // this.isselectedFields = true;
      }
		}).catch((error) => {
      if (error != "0") {
        // console.log(error);
      }      
		});
	}
  
  opennotesModal(searchRequestId: number) {
		const modalRef = this.modalService.open(RequestNotesComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });    
    modalRef.componentInstance.searchRequestId = searchRequestId;
    if(this.isClosed) {
      modalRef.componentInstance.isdisabled = true;
    }
		modalRef.result.then((result) => {    

		}).catch((error) => {
      if (error != "0") {
        // console.log(error);
      }      
		});
	}
}
