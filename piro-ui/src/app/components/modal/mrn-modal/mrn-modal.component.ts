import { Component, OnInit } from '@angular/core';
import { PatientService } from '../../../services/patient.service';
import { LocalStorageService } from '../../../services/localStorage.service';
import { ToastrService } from 'ngx-toastr';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-mrn-modal',
  templateUrl: './mrn-modal.component.html',
  styleUrls: ['./mrn-modal.component.css']
})
export class MrnModalComponent implements OnInit {
  dataloaded: boolean = false;
  isDisabled: boolean = false;
  isSearch: boolean = false;
  isSelected: boolean = false;
  mrnText: string = '';
  items: any = [];
  loaded: boolean = true;
  constructor(private activeModal: NgbActiveModal,
    private patientService: PatientService,
    private localStorage: LocalStorageService,
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService) {
  }

  async ngOnInit() {
    this.mrnText = this.localStorage.getMrn();
    if (this.mrnText != '') {
      this.search();
    }
  }

  async search() {
    if (this.mrnText == "") {
      this.toastr.error('', 'MRN text is mandatory');
      return;
    }
    this.loaded = false;
    this.isSearch = false;
    this.isSelected = false;
    const result = await this.patientService.searchMrn(this.mrnText);
    if (result.status == true) {
      this.items = result.data;
      this.isSearch = true;
      this.loaded = true;
      if (this.items.length > 0) {
        this.isSelected = true;
      }
    }
  }

  saveModal() {
    this.localStorage.setMrn(this.mrnText);
    this.activeModal.close(true);
  }

  clearModal() {
    this.localStorage.clearItem("mrn");
    this.loaded = true;
    this.isSearch = false;
    this.isSelected = false;
  }

  closeModal() {
    this.activeModal.close(true);
  }
}
