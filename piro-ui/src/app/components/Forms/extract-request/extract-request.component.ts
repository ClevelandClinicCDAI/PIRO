import { Component, inject } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { ExtractRequestService } from '../../../services/extract-request.service';
import { SavedSearchContentService } from 'src/app/services/saved-search-content.service';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { NgbAlertModule, NgbDatepickerModule, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from 'src/app/services/auth.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ExportfieldComponent } from '../../modal/exportfield/exportfield.component';
import { DataService } from '../../../services/data.service';

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
  constructor(private modalService: NgbModal,
    private formBuilder: FormBuilder,
    private extractRequestService: ExtractRequestService,
    private savedSearchService: SavedSearchContentService,
    private confirmDialogService: ConfirmDialogService,
    private authService: AuthService,
    private dataService: DataService,
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
      dateFrom: ['', [Validators.required]],
      dateTo: ['', [Validators.required]],
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
      this.dataRequestForm.get('isPediatric').updateValueAndValidity();
      this.isirb = false;
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
      // this.isdateValid = this.dateFrom != null && this.dateTo != null;
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


    var dFrom = this.dataRequestForm.get('dateFrom').value;
    var dTo = this.dataRequestForm.get('dateTo').value;
    if ((new Date(dFrom.year, dFrom.month, dFrom.day)) > (new Date(dTo.year, dTo.month, dTo.day))) {
      this.toastr.error('Date range is invalid', 'Error');
      this.contentLoaded = true;
      return;
    }


    let that = this;
    this.confirmDialogService.confirmClassThis('<legal disclaimer here>.',
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
      // console.log(JSON.stringify(this.dataRequestForm.get('dateFrom').value));
      var dFrom = this.dataRequestForm.get('dateFrom').value;
      var dTo = this.dataRequestForm.get('dateTo').value;
      // console.log(`${dFrom.year}-${dFrom.month}-${dFrom.day}`);
      // console.log(JSON.stringify(this.dataRequestForm.get('dateTo').value));
      const formData: FormData = new FormData();
      formData.append('name', this.dataRequestForm.get('name').value);
      formData.append('comment', this.dataRequestForm.get('comment').value);
      formData.append('searchId', this.dataRequestForm.get('searchId').value);
      formData.append('reasonId', this.dataRequestForm.get('reasonId').value);
      formData.append('isPediatric', this.dataRequestForm.get('isPediatric').value);
      formData.append('irb', this.dataRequestForm.get('irbNumber').value);
      formData.append('selectedFields', this.selectedFields.map(function (item: any) { return item.datafieldId; }));
      formData.append('dateTo', `${dTo.year}-${dTo.month}-${dTo.day} 00:00:00`);
      formData.append('dateFrom', `${dFrom.year}-${dFrom.month}-${dFrom.day} 00:00:00`);
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
