import { Component } from '@angular/core';

import { environment } from '../../../environments/environment';
import { Common } from '../../helpers';
import { ToastrService } from 'ngx-toastr';
import { ConfirmDialogService } from '../../services/confirm-dialog.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AddcohortComponent } from './addcohort/addcohort.component';
import { EditcohortComponent } from './editcohort/editcohort.component';
import { CohortService } from '../../services/cohort.service';
import { HttpResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';
@Component({
  standalone: false,
  selector: 'app-cohort',
  templateUrl: './cohort.component.html',
  styleUrls: ['./cohort.component.css']
})
export class CohortComponent {
  items: any = [];
  page: number = 1;
  count: number = 0;
  tableSize: number = environment.recordsPerPage;
  tcommon: Common;
  contentText: string = "";
  contentLoaded = true;
  subscription!: Subscription;
  constructor(
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService,
    private router: Router,
    private modalService: NgbModal,
    private activatedRoute: ActivatedRoute,
    private cohortService: CohortService,
    private common: Common) {
    this.tcommon = common
  }
  ngOnInit() {
    this.getAll();
    this.subscription = this.cohortService.getStatusCount().subscribe((data: any) => {
      if (data.status) {
        this.getAll();
      } else {
      }
    });
  }

  async getAll() {
    this.contentLoaded = false;
    const result = await this.cohortService.getAll();
    if (result.status == true) {
      this.items = result.data;
      this.contentLoaded = true;
    } else {
      this.toastr.error('', 'Something went wrong.');
      this.contentLoaded = true;
    }
  }


  openAddNew() {
    const modalRef = this.modalService.open(AddcohortComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
    modalRef.result.then((result) => {

    }).catch((error) => {
      if (error != 1) {
        this.toastr.error('', 'Something went wrong.');
      }
    });
  }

  async delete(cohortId: number, name: string) {
    let that = this;
    this.confirmDialogService.confirmThis(`Are you sure you want to delete this cohort (${name})?`, async function () {
      const result: any = await that.cohortService.delete(cohortId);
      if (result.status == true) {
        that.getAll();
        that.toastr.success('', 'Cohort deleted successfully.');
      } else {
        that.toastr.error('', 'Something went wrong.');
      }
    }, function () {

    })

  }

  async download(cohortId: number, name: string) {
    (await this.cohortService.export(cohortId)).subscribe(async (event: any) => {
      const data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });

      let fileName = `${name.replaceAll(" ", "_")}.xlsx`;
      const a = document.createElement('a');
      a.setAttribute('style', 'display:none;');
      document.body.appendChild(a);
      a.download = fileName;
      a.href = URL.createObjectURL(downloadedFile);
      a.target = '_blank';
      a.click();
      document.body.removeChild(a);
    },
    error => {
      this.toastr.error('', 'Something went wrong.');
    },);

  }

  async exportCaseTemplate() {
    (await this.cohortService.exportCaseTemplate()).subscribe(async (event: any) => {
      const data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });

      let fileName = "CohortCaseTemplate.xlsx";
      const a = document.createElement('a');
      a.setAttribute('style', 'display:none;');
      document.body.appendChild(a);
      a.download = fileName;
      a.href = URL.createObjectURL(downloadedFile);
      a.target = '_blank';
      a.click();
      document.body.removeChild(a);
    },
    error => {
      this.toastr.error('', 'Something went wrong.');
    },);
  }

  async exportMRNTemplate() {
    (await this.cohortService.exportMRNTemplate()).subscribe(async (event: any) => {
      const data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });

      let fileName = "CohortMRNTemplate.xlsx";
      const a = document.createElement('a');
      a.setAttribute('style', 'display:none;');
      document.body.appendChild(a);
      a.download = fileName;
      a.href = URL.createObjectURL(downloadedFile);
      a.target = '_blank';
      a.click();
      document.body.removeChild(a);
    },
    error => {
      this.toastr.error('', 'Something went wrong.');
    },);
  }

  async exportEIDTemplate() {
    (await this.cohortService.exportEIDTemplate()).subscribe(async (event: any) => {
      const data = event as HttpResponse<Blob>;
      const downloadedFile = new Blob([data.body as BlobPart], {
        type: data.body?.type
      });

      let fileName = "CohortEIDTemplate.xlsx";
      const a = document.createElement('a');
      a.setAttribute('style', 'display:none;');
      document.body.appendChild(a);
      a.download = fileName;
      a.href = URL.createObjectURL(downloadedFile);
      a.target = '_blank';
      a.click();
      document.body.removeChild(a);
    },
    error => {
      this.toastr.error('', 'Something went wrong.');
    },);
  }

  async editcohort(id: number) {
    const modalRef = this.modalService.open(EditcohortComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
    modalRef.componentInstance.id = id;

    modalRef.result.then((result) => {

    }).catch((error) => {
      if (error != 1) {
        this.toastr.error('', 'Something went wrong.');
      }
    });
  }


}
