import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { SavesearchService } from '../../../services/savesearch.service';
import { LocalStorageService } from '../../../services/localStorage.service';
import { SearchService } from '../../../services/search.service';

@Component({
  standalone: false,
	selector: 'app-savesearchmodal',
	templateUrl: './savesearchmodal.component.html',
	styleUrls: ['./savesearchmodal.component.css']
})
export class SavesearchmodalComponent {

	saveSearchForm: any = FormGroup;
	submitted = false;
	query: string = ''
	get f() { return this.saveSearchForm.controls; }

	constructor(private activeModal: NgbActiveModal,
		private formBuilder: FormBuilder,
		private saveSearchService: SavesearchService,
		private searchService: SearchService,
		private toastr: ToastrService,
		private router: Router,
		private localStorageService: LocalStorageService) {
		this.createForm();
	}



	createForm() {

	}

	async submitForm() {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveSearchForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted) {
			var advfields = this.localStorageService.getAdancedFilterData();
			var mrn = this.localStorageService.getMrn();
			const res: any = await this.saveSearchService.saveSearch(this.saveSearchForm.value, advfields, mrn);

			if (res.status == true) {
				this.toastr.success('', 'Search added successfully.');
				this.activeModal.close('Modal Closed');
			} else if (res.status == false) {
				this.toastr.error('', res.err);
			} else {
				this.toastr.error('', 'Something went wrong.');
			}
		}
	}

	async ngOnInit() {
		this.query = window.location.pathname + window.location.search;
		this.saveSearchForm = this.formBuilder.group({
			name: ['', [Validators.required]],
			description: [''],
			query: [this.query, [Validators.required]]
		});
		var filter = this.localStorageService.getFilter();
		var filteredItems = "";
		var filteredString = "";
		if (filter.length > 0) {
			filter.forEach((element: any) => {
				filteredItems += element.field + ": " + element.search + '\n';
				filteredString += element.search + "_";
			});
		}
		if (filteredString != "") {
			filteredString = filteredString.replace(/_+$/, '');
		}
		this.saveSearchForm.controls['name'].setValue(filteredString);

		//Fetch advanced search
		var advFilter = this.localStorageService.getAdancedFilterData();
		const result: any = await this.searchService.validateAdvancedFilter(advFilter);
		if (result.status == true) {
			let that = this;
			if (result.data.result) {
				filteredItems = filteredItems + 'Advanced Search: ' + result.data.filter + '\n';
			}
		}

		var mrn = this.localStorageService.getMrn();
		if (mrn != '') {
			filteredItems = filteredItems + 'MRN Search: ' + mrn;
		}

		this.saveSearchForm.controls['description'].setValue(filteredItems);
	}

	closeModal() {
		this.activeModal.close('Modal Closed');
	}	 
}
