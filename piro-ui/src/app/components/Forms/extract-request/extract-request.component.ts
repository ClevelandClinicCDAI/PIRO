import { Component, inject } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { ExtractRequestService } from '../../../services/extract-request.service';
import { SavedSearchContentService } from 'src/app/services/saved-search-content.service';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ExportfieldComponent } from '../../modal/exportfield/exportfield.component';
import { DataService } from '../../../services/data.service';
import { SavesearchService } from 'src/app/services/savesearch.service';
import { AppConfigService } from '../../../services/app-config.service';

@Component({
  selector: 'app-extract-request',
  templateUrl: './extract-request.component.html',
  styleUrls: ['./extract-request.component.css'],
  // standalone: true,
  // imports: [NgbDatepickerModule, NgbAlertModule],
})
export class ExtractRequestComponent {

  dataRequestForm: any = FormGroup;
  submitted = false;
  searches: any = [];
  reasons: any = [];
  userName: string = "";
  role: string = "";
  contentLoaded = true;
  selectedFields: any = [];
  isfileValid: boolean = false;
  isselectedFields: boolean = false;
  isirb: boolean = false;
  pediatricFilterError: string = "";
  collectionDateFilterError: string = "";
  constructor(private modalService: NgbModal,
    private formBuilder: FormBuilder,
    private extractRequestService: ExtractRequestService,
    private savedSearchService: SavedSearchContentService,
    private saveSearchService: SavesearchService,
    private confirmDialogService: ConfirmDialogService,
    private authService: AuthService,
    private dataService: DataService,
    private appConfigService: AppConfigService,
    private toastr: ToastrService, private router: Router) {
  }


  async ngOnInit(): Promise<void> {
    //Add Data Extract Request Form Validations
    this.dataRequestForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      searchId: ['', [Validators.required]],
      comment: ['', [Validators.required]],
      reasonId: ['', [Validators.required]],
      request_file: ['', [Validators.nullValidator]],
      irbNumber: ['', [Validators.required]],
      isPediatric: ['', [Validators.required]]
    });
    this.searches = await this.savedSearchService.getDropdownContentFromDB();
    this.reasons = await this.extractRequestService.getDropdownReasonsFromDB();
    var auth: any = await this.authService.getUser();
    this.userName = auth.name;
    this.role = auth.role;
  }

  get f() { return this.dataRequestForm.controls; }
  file: any = null;
  uploadFile(e: any) {
    this.file = e.target.files[0];
    this.isfileValid = this.file != null;
    // console.log(`onFileSelected(${this.file.name})`)
  }

  onReasonChange() {
    this.pediatricFilterError = "";
    this.collectionDateFilterError = "";
    var reasonId = this.dataRequestForm.get('reasonId').value;
    const reason = this.reasons.data.filter((r: any) => { return r.value.toLocaleString() === reasonId });
    if (reason.length > 0 && reason[0].code === "IRB") {
      this.dataRequestForm.get('irbNumber').setValidators([Validators.required]);
      this.dataRequestForm.get('irbNumber').updateValueAndValidity();

      this.dataRequestForm.get('isPediatric').setValidators([Validators.required]);
      this.dataRequestForm.get('isPediatric').updateValueAndValidity();
      this.isirb = true;
    } else {
      this.dataRequestForm.get('irbNumber').clearValidators();
      this.dataRequestForm.get('irbNumber').updateValueAndValidity();

      this.dataRequestForm.get('isPediatric').clearValidators();
      this.dataRequestForm.get('isPediatric').setValue('');
      this.dataRequestForm.get('isPediatric').updateValueAndValidity();
      this.isirb = false;
    }
  }

  async onSearchChange() {
    this.pediatricFilterError = "";
    this.collectionDateFilterError = "";
    if (this.isirb) {
      await this.validateCollectionDateSelection();
    }
    if (this.isirb && this.dataRequestForm.get('isPediatric').value === '0') {
      await this.validatePediatricSelection();
    }
  }

  async onIsPediatricChange() {
    this.pediatricFilterError = "";
    if (this.isirb && this.dataRequestForm.get('isPediatric').value === '0') {
      await this.validatePediatricSelection();
    }
  }

  async validatePediatricSelection() {
    const hasAgeFilter = await this.hasCasePatientAgeFilter();
    if (!hasAgeFilter) {
      this.pediatricFilterError = "You must have an age filter in your search to exclude pediatric patients";
      this.dataRequestForm.get('isPediatric').setValue('');
      this.dataRequestForm.get('isPediatric').markAsTouched();
      this.dataRequestForm.get('isPediatric').updateValueAndValidity();
      return false;
    }
    return true;
  }

  async hasCasePatientAgeFilter() {
    const searchId = this.dataRequestForm.get('searchId').value;
    if (!searchId) {
      return false;
    }
    const result: any = await this.saveSearchService.getSearch(searchId);
    if (result.status != true || !result.data?.query) {
      return false;
    }
    return this.queryHasCasePatientAgeFilter(result.data.query);
  }

  queryHasCasePatientAgeFilter(query: string) {
    try {
      const queryString = query.includes('?') ? query.split('?')[1] : query;
      const searchParams = new URLSearchParams(queryString);
      const searchFilter = searchParams.get('searchFilter');
      if (!searchFilter) {
        return query.includes('casepatientageyears');
      }
      const filters = JSON.parse(searchFilter);
      if (!Array.isArray(filters)) {
        return false;
      }
      return filters.some((item: any) => item?.field === 'casepatientageyears');
    } catch (error) {
      return query.includes('casepatientageyears');
    }
  }

  async validateCollectionDateSelection() {
    const hasFilter = await this.hasCollectionDateFilter();
    if (!hasFilter) {
      this.collectionDateFilterError = "For IRB approved research, there must be a collection date filter that matches your IRB-approved date range";
      return false;
    }
    return true;
  }

  async hasCollectionDateFilter() {
    const searchId = this.dataRequestForm.get('searchId').value;
    if (!searchId) {
      return false;
    }
    const result: any = await this.saveSearchService.getSearch(searchId);
    if (result.status != true || !result.data?.query) {
      return false;
    }
    return this.queryHasCollectionDateFilter(result.data.query);
  }

  queryHasCollectionDateFilter(query: string) {
    try {
      const queryString = query.includes('?') ? query.split('?')[1] : query;
      const searchParams = new URLSearchParams(queryString);
      const searchFilter = searchParams.get('searchFilter');
      if (!searchFilter) {
        return query.includes('collectiondate');
      }
      const filters = JSON.parse(searchFilter);
      if (!Array.isArray(filters)) {
        return false;
      }
      return filters.some((item: any) => item?.field === 'collectiondate');
    } catch (error) {
      return query.includes('collectiondate');
    }
  }

  async onSubmit() {
    this.submitted = true;
    this.contentLoaded = false;
    // console.log(this.reasons.data);
    var reasonId = this.dataRequestForm.get('reasonId').value;
    const reason = this.reasons.data.filter((r: any) => { return r.value.toLocaleString() === reasonId });
    // console.log(reason[0]);
    if (reason.length > 0 && reason[0].code === "IRB") {
      this.isfileValid = this.file != null;
      if (!this.isfileValid) {
        this.contentLoaded = true;
        return;
      }
    } else {
      this.isfileValid = true;
    }

    if (this.selectedFields.length > 0) {
      this.isselectedFields = true;
    } else {
      this.contentLoaded = true;
      return;
    }

    if (this.isirb && this.dataRequestForm.get('isPediatric').value === '0') {
      const hasAgeFilter = await this.hasCasePatientAgeFilter();
      if (!hasAgeFilter) {
        this.pediatricFilterError = "You must have an age filter in your search to exclude pediatric patients";
        this.dataRequestForm.get('isPediatric').setValue('');
        this.dataRequestForm.get('isPediatric').updateValueAndValidity();
        this.contentLoaded = true;
        return;
      }
    }

    if (this.isirb) {
      const hasCollectionDate = await this.hasCollectionDateFilter();
      if (!hasCollectionDate) {
        this.collectionDateFilterError = "For IRB approved research, there must be a collection date filter that matches your IRB-approved date range";
        this.contentLoaded = true;
        return;
      }
    }



    // stop here if form is invalid
    if (this.dataRequestForm.invalid) {
      this.contentLoaded = true;
      return;
    }

    var validExtensions: string[] = ['pdf'];
    if (this.file) {
      var fileNameExt: string = this.file.name.substr(this.file.name.lastIndexOf('.') + 1);
      if (!validExtensions.includes(fileNameExt.toLowerCase())) {
        this.toastr.error('File uploaded should be PDF', 'Error');
        this.contentLoaded = true;
        return;
      }
    }

    let that = this;
    this.confirmDialogService.confirmClassThis(this.appConfigService.irbDisclaimerText,
      'custom-alert-lg',
      async function () {
        that.submitForm();
      }, function () {
        that.contentLoaded = true;
      });
    //True if all the fields are filled

  }

  async submitForm() {
    if (this.submitted) {
      const formData: FormData = new FormData();
      formData.append('name', this.dataRequestForm.get('name').value);
      formData.append('comment', this.dataRequestForm.get('comment').value);
      formData.append('searchId', this.dataRequestForm.get('searchId').value);
      formData.append('reasonId', this.dataRequestForm.get('reasonId').value);
      formData.append('isPediatric', this.dataRequestForm.get('isPediatric').value);
      formData.append('irb', this.dataRequestForm.get('irbNumber').value);
      formData.append('selectedFields', this.selectedFields.map(function (item: any) { return item.datafieldId; }));
      formData.append('file', this.file);
      const res: any = await this.extractRequestService.createRequest(formData, this.file != null);
      // console.log("upload done?")

      if (res.status == true) {
        this.toastr.success('', 'Data request added successfully.');
        this.contentLoaded = true;
        if (this.role == 'ADMIN' || this.role == 'DEMOADMIN' || this.role == 'ANALYST') {
          this.router.navigate(['my-requests']);
        } else {
          this.router.navigate(['home']);
        }
      } else if (res.status == false) {
        this.contentLoaded = true;
        this.toastr.error('', res.err);
      } else {
        this.contentLoaded = true;
        this.toastr.error('', 'Something went wrong.');
      }
    }
  }

  openexportfieldModal() {
    const modalRef = this.modalService.open(ExportfieldComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
    modalRef.componentInstance.inSelectedFields = this.selectedFields;
    modalRef.componentInstance.isCreate = true;
    modalRef.result.then((result) => {
      // console.log(result);
      if (result.length > 0) {
        this.selectedFields = result;
        this.isselectedFields = true;
      }
    }).catch((error) => {
      if (error != "0") {
        console.log(error);
      }
    });
  }
}
