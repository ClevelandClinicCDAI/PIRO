import { Component, Input } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { SaveTagService } from '../../../services/save-tag.service';
import { CreatetagComponent } from '../createtag/createtag.component';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-tag',
  templateUrl: './tag.component.html',
  styleUrls: ['./tag.component.css']
})
export class TagComponent {
  	@Input() public CaseId:number = 0;
	@Input() public CaseNum:string = '';
  	saveTagForm: any = FormGroup;
	submitted = false;
	query:string = ''
	get f() { return this.saveTagForm.controls; }
	items: any = [];
	tagsDropdown:any = [];
	constructor(private modalService: NgbModal,
		private activeModal: NgbActiveModal, 
		private formBuilder: FormBuilder, 
		private saveTagService: SaveTagService, 
		private toastr: ToastrService, 
		private router: Router,
		private confirmDialogService: ConfirmDialogService) {
		
	}

	async submitForm(formDirective:any) {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveTagForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted) {
			const res: any = await this.saveTagService.saveCaseTag(this.saveTagForm.value);
			if (res.status == true) {
				this.toastr.success('', 'Tag added successfully.');
				//formDirective.resetForm();
				//this.submitted = false; 
				this.getAll();
				} else if (res.status == false) {
				this.toastr.error('', res.err);
			} else {
				this.toastr.error('', 'Something went wrong.');
			}
		}
	}

	ngOnInit() {
		this.saveTagForm = this.formBuilder.group({
			tagid: ['', [Validators.required]],
      		caseid:this.CaseId
		});
		this.getTagDropdown();
		this.getAll();
	}

	closeModal() {
		this.activeModal.close('Modal Closed');
		this.saveTagService.setStatusCount(true);
	}


	openCreateTag(){
		this.activeModal.close('Modal Closed');
		const modalRef = this.modalService.open(CreatetagComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
    	modalRef.componentInstance.CaseId = this.CaseId;
		modalRef.result.then((result) => {
      
		}).catch((error) => {

		});
	}
	async getTagDropdown(){
		const result = await this.saveTagService.getTagDropdown();
		if(result.status == true){
		  this.tagsDropdown = result.data;
		}
	}
	async getAll(){
		const result = await this.saveTagService.getCaseTagContent(this.CaseId);
		if(result.status == true){
		  this.items = result.data;
		}
	}
	deleteTag(id:number){
		let that = this;
		this.confirmDialogService.confirmThis("Are you sure to delete?", async function () {  
		const result:any = await that.saveTagService.deleteCaseTag(id);
		if(result.status == true){
			that.toastr.success('','Tag deleted successfully.');
			that.getAll();
		}else{
			that.toastr.error('','Something went wrong.');
		}
		}, function () {  
		
		})  
	}

}
