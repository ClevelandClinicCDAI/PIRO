import { Component } from '@angular/core';
import { AivoteService } from '../../services/aivote.service';
import { environment } from '../../../environments/environment';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { SearchService } from '../../services/search.service';
import { ConfirmDialogService } from '../../services/confirm-dialog.service';
import { ToastrService } from 'ngx-toastr';
import { FormBuilder, FormGroup } from '@angular/forms';
import { AireviewcasedetailComponent } from '../modal/aireviewcasedetail/aireviewcasedetail.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
@Component({
  standalone: false,
  selector: 'app-aireviews',
  templateUrl: './aireviews.component.html',
  styleUrls: ['./aireviews.component.css']
})
export class AireviewsComponent {
  items: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;
  annotationConfig: any = [];

  aiReviewFilterForm:any = FormGroup;
  data: any = {};

  constructor(private modalService: NgbModal,private formBuilder: FormBuilder,private aiVoteService:AivoteService,private router: Router, private searchService: SearchService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService,
    private activatedRoute: ActivatedRoute){}
  ngOnInit(){
    this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
      this.page = parseInt(params.get('page') || '1');
    });
    this.getConfig();
    this.defaultSearch();
    this.data = this.aiReviewFilterForm.value;
    this.getAll();
  }

  defaultSearch() {
    this.aiReviewFilterForm = this.formBuilder.group({
      annotationConfigurationId : [-1],
      caseid: [-1],
      casenum: [''],
      feedback: [-1],
      pending: [true]
    });
  }

  get f() { return this.aiReviewFilterForm.controls; }

  async getConfig() {
		const result = await this.searchService.getAnnotationConfig();
		if (result.status == true) {
			this.annotationConfig = result.data;
		}
	}

  async getAll(){
    const result = await this.aiVoteService.getAll(this.page, this.tableSize, this.data);
    if(result.status == true){
      this.items = result.data?.items;
      this.count = result.data?.total;
    }
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


  clearFilter() {
    this.page = 1;
    this.defaultSearch();
    this.data = this.aiReviewFilterForm.value;
    this.getAll();
	}

  reviewFeedback(id: number) {
		let that = this;
		this.confirmDialogService.confirmThis("Are you sure to close the review?", async function () {
		const result: any = await that.aiVoteService.markReviewed(id);
		if (result.status == true) {
      that.page = 1;
			that.getAll();
		} else {
			that.toastr.error('', 'Something went wrong.');
		}
		}, function () {

		});
	}

  async onSubmit() {
      this.page = 1;
      this.data = this.aiReviewFilterForm.value
      this.getAll();
  }

  openCaseDetail(caseid: number, casemum: string) {
		const modalRef = this.modalService.open(AireviewcasedetailComponent, { ariaLabelledBy: 'modal-basic-title', size: 'xl', scrollable: true });
    modalRef.componentInstance.caseIdInput = caseid;
    modalRef.componentInstance.caseNum = casemum;
    
		modalRef.result.then((result) => {

		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}
}
