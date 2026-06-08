import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ToastService } from '../../../services/toast.service';
import { Router } from '@angular/router';
import { LocalStorageService } from '../../../services/localStorage.service';
import { SearchService } from '../../../services/search.service';
import { CohortService } from '../../../services/cohort.service';

@Component({
  standalone: false,
	selector: 'app-addcohort',
	templateUrl: './addcohort.component.html',
	styleUrls: ['./addcohort.component.css']
})
export class AddcohortComponent {
	saveForm: any = FormGroup;
	submitted = false;
	query: string = ''
	get f() { return this.saveForm.controls; }
	isfileValid: boolean = false;
	file: any = null;
	contentLoaded: boolean = true;
	contentText: string = "";
	dataTypes: any = [];

	constructor(private activeModal: NgbActiveModal,
		private formBuilder: FormBuilder,
		private cohortService: CohortService,
		private toastService: ToastService,
		private toastr: ToastrService) {

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
	}

	async ngOnInit() {
		this.query = window.location.pathname + window.location.search;
		this.saveForm = this.formBuilder.group({
			name: ['', [Validators.required]],
			desc: ['', [Validators.required]],
			disease: ['-'],
			display: [true],
			dataType: ['', [Validators.required]],
			request_file: ['', [Validators.nullValidator]]
		});
	}

	async submitForm() {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted && this.isfileValid) {
			this.contentLoaded = false;
			const formData: FormData = new FormData();
			formData.append('name', this.saveForm.get('name').value);
			formData.append('desc', this.saveForm.get('desc').value);
			formData.append('file', this.file);
			formData.append("cohortId", "-1");
			var disease = (this.saveForm.get('disease').value || '') == '' ? '-' : this.saveForm.get('disease').value;
			formData.append("disease", disease);
			formData.append("display", this.saveForm.get('display').value);
			formData.append("dataType", this.saveForm.get('dataType').value);
			const res: any = await this.cohortService.createRequest(formData, this.isfileValid);

			if (res.status == true && res.data == true) {
				this.toastr.success('', 'Cohort added successfully.');
				this.cohortService.setStatusCount(true);
				this.activeModal.close('Modal Closed');
				this.contentLoaded = true;
			} else if (res.status == true && res.data == false) {
				// this.toastr.error('', 'Error in the cohort creation process. Please review the cohort created and take necessary action.');
				this.toastService.showErrorToast('Error', 'Error in the cohort creation process. Please review the cohort created and take necessary action.', []);
				this.cohortService.setStatusCount(true);
				this.activeModal.close('Modal Closed');
				this.contentLoaded = true;
			}
			else if (res.status == false) {
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
