import { Component, Input } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, ReactiveFormsModule, Validators, NgForm } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { SaveTagService } from 'src/app/services/save-tag.service';
import { environment } from '../../../../environments/environment';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { TagComponent } from '../tag/tag.component';

@Component({
  selector: 'app-createtag',
  templateUrl: './createtag.component.html',
  styleUrls: ['./createtag.component.css']
})
export class CreatetagComponent {
	@Input() public CaseId:number  =0;
	saveCreateTagForm: any = FormGroup;
	submitted = false;
	query:string = ''
	get f() { return this.saveCreateTagForm.controls; }
	items: any = [];
	page: number = 1;
	count: number = 0;
	tableSize: number = environment.recordsPerPage;
	constructor(private modalService: NgbModal,private activeModal: NgbActiveModal, private formBuilder: FormBuilder, private saveTagService: SaveTagService, private toastr: ToastrService, private router: Router,private confirmDialogService: ConfirmDialogService) {
		this.createForm();
	}

	

	createForm() {
	}

	async submitForm(formDirective:any) {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveCreateTagForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted) {
			const res: any = await this.saveTagService.saveTag(this.saveCreateTagForm.value);
			if (res.status == true) {
				this.toastr.success('', 'Tag added successfully.');
				formDirective.resetForm();
				this.submitted = false; 
				this.getAll();	

			} else if (res.status == false) {
				this.toastr.error('', res.err);
			} else {
				this.toastr.error('', 'Something went wrong.');
			}
		}
	}

	ngOnInit() {
		this.saveCreateTagForm = this.formBuilder.group({
			name: ['', [Validators.required]],
			description:['']
		});
		this.getAll();
	}

	async getAll(){
		const result = await this.saveTagService.getContent(this.page,this.tableSize);
		if(result.status == true){
		  this.items = result.data?.items;
		  this.count = result.data?.total;
		}
	}

	closeModal() {
		this.activeModal.close('Modal Closed');
		const modalRef = this.modalService.open(TagComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
		modalRef.componentInstance.CaseId = this.CaseId;
		modalRef.result.then((result) => {
		
		}).catch((error) => {

		});
	}

	deleteTag(id:number){
		let that = this;
		this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
		const result:any = await that.saveTagService.deleteTag(id);
		if(result.status == true){
			that.page = 1;
			that.count = 0;
			that.toastr.success('','Tag deleted successfully.');
			that.getAll();
		}else{
			that.toastr.error('','Something went wrong.');
		}
		}, function () {  
		
		})  
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
	
}
