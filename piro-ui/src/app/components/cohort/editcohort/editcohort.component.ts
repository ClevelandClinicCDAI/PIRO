import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ToastService } from '../../../services/toast.service';
import { Router } from '@angular/router';
import { SavesearchService } from '../../../services/savesearch.service';
import { LocalStorageService } from '../../../services/localStorage.service';
import { SearchService } from '../../../services/search.service';
import { CohortService } from 'src/app/services/cohort.service';
@Component({
	selector: 'app-editcohort',
	templateUrl: './editcohort.component.html',
	styleUrls: ['./editcohort.component.css']
})
export class EditcohortComponent {
	@Input() public id: any;
	saveForm: any = FormGroup;
	submitted = false;
	query: string = ''
	get f() { return this.saveForm.controls; }
	isfileValid: boolean = false;
	file: any = null;
	item: any = {};
	contentLoaded: boolean = true;
	contentText: string = "";
	dataTypes: any = [];
	cohortType: string = ''
	controlEnabled = new FormControl(false);
	
	constructor(private activeModal: NgbActiveModal,
		private formBuilder: FormBuilder,
		private cohortService: CohortService,
		private toastr: ToastrService,
		private toastService: ToastService,
		private router: Router,
		private localStorageService: LocalStorageService) {
		this.dataTypes = [{
			"text": "MRN",
			"value": "P"
		},
		{
			"text": "Case",
			"value": "C"
		},
		{
			"text": "EID",
			"value": "E"
		}];
		this.createForm();
	}


	async ngOnInit() {
		this.saveForm = this.formBuilder.group({
			cohortId: [-1],
			caseCount: [0],
			patientCount: [0],
			matched: [0],
			unmatched: [0],
			name: ['', [Validators.required]],
			desc: ['', [Validators.required]],
			disease: ['-'],
			display: [true],
			dataType: [''],
			request_file: ['', [Validators.nullValidator]]
		});

		var res = await this.cohortService.getDataById(this.id);


		if (res.status == true) {
			this.item = res.data;
			this.cohortType = res.data.dataType;
			this.saveForm.patchValue(res.data);
			// this.saveForm.controls.desc.setValue(res.data.desc);
			this.saveForm.get('dataType').disable();
		}
		
		
	}

	createForm() {
	}

	async submitForm() {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted) {
			this.contentLoaded = false;
			const formData: FormData = new FormData();
			formData.append('name', this.saveForm.get('name').value);
			formData.append('desc', this.saveForm.get('desc').value);
			formData.append('file', this.file);
			formData.append("cohortId", this.id);
			formData.append("disease", this.saveForm.get('disease').value);
			formData.append("display", this.saveForm.get('display').value);
			formData.append("dataType", this.saveForm.get('dataType').value);
			const res: any = await this.cohortService.createRequest(formData, this.isfileValid);
			// if (res.status == true) {
			// 	this.toastr.success('', 'Cohort updated successfully.');
			// 	this.cohortService.setStatusCount(true);
			// 	this.activeModal.close('Modal Closed');
			// 	this.contentLoaded = true;
			// } 
			
			if (res.status == true && res.data == true) {
				this.toastr.success('', 'Cohort added successfully.');
				this.cohortService.setStatusCount(true);
				this.activeModal.close('Modal Closed');
				this.contentLoaded = true;
			} else if (res.status == true && res.data == false) {
				// this.toastr.error('', 'Error in the cohort creation process. Please review the cohort created and take necessary action.');
				this.toastService.showErrorToast('Error', 'Error in the cohort creation process. Please review the cohort created and take necessary action.', []);
				// this.showoast(EventTypes.Error, err?.error, []);
				this.cohortService.setStatusCount(true);
				this.activeModal.close('Modal Closed');
				this.contentLoaded = true;
			} else if (res.status == false) {
				//this.toastr.error('', res.err);
				this.contentLoaded = true;
			} else {
				this.toastr.error('', 'Something went wrong.');
				this.contentLoaded = true;
			}
		}
	}

	closeModal() {
		this.activeModal.close('Modal Closed');
	}

	uploadFile(e: any) {
		this.file = e.target.files[0];
		this.isfileValid = this.file != null;
	}
}
