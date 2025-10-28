import { Component, Injector, Input } from '@angular/core';
import { SearchService } from '../../../services/search.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-synoptic-epic',
  templateUrl: './synoptic-epic.component.html',
  styleUrls: ['./synoptic-epic.component.css']
})
export class SynopticEpicComponent {
  specimensGroup: any = [];
  specimens: any = [];
  contentLoaded = false;
  activeModal!: NgbActiveModal;
  synopticlistId: string = '';
  versionDate: any = null;
  synopticComments: any = [];
  synopticReports: any = [];
  patientComments: any = [];  
  synopticlist: any = [];
  parsed:  boolean = false;

  @Input() caseId: string = "-1";

  @Input() isModal: boolean = false;
  constructor(private injector: Injector,
    //private activeModal: NgbActiveModal,
    private searchService: SearchService,
    private toastr: ToastrService) {
  }

  async ngOnInit() {
    if (this.isModal) {
      this.activeModal = <NgbActiveModal>this.injector.get(NgbActiveModal);
    }
    this.contentLoaded = false;
    const result = await this.searchService.getCaseDetail(this.caseId);
    if (result.status == true) {
      this.specimensGroup = result.data.specimensGroup;
      this.specimens = result.data.specimens;
      this.specimensGroup.forEach((item: any) => {
        item.specimens = item.specimenGrp.split(',');
        item.ids = item.synopticId.split(',');
        item.isSpecimenLevel = item.isSpecimenLevel;
      });
      this.synopticlistId = this.specimensGroup.length > 0 ? this.specimensGroup[0].synopticId : '-';
      this.getSynopticText(this.synopticlistId);
    }
    this.contentLoaded = true;
  }

  async buildSynopticDataSource(synopticlistId: any) {
    var that = this;
    that.synopticlist = [];
    var synopticlistIds = synopticlistId.split(',');
    synopticlistIds.forEach((currentValue: any, index: number) => {
      that.synopticlist.push({ text: 'Version ' + (synopticlistIds.length - index), id: currentValue });
    });
    // console.log(that.synopticlist);
  }

  async onSynopticChange(event: any) {    
    this.getSynopticTextForId(event.target.value);
  }

  async getSynopticText(synopticlistId: any) {
    this.contentLoaded = false;
    this.synopticlistId = synopticlistId;
    this.buildSynopticDataSource(synopticlistId);
    this.getSynopticTextForId(synopticlistId.split(',')[0]);
  }

  async getSynopticTextForId(synopticId: any) {
    // console.log(event);
    this.contentLoaded = false;

    var synData = this.specimens.filter((p: any) => p.synopticId == synopticId);
    // console.log(synData);
    if (synData.length > 0) {
      this.versionDate = synData[0].recordDate;
    }
    const result = await this.searchService.getSynopticComments(synopticId);
    if (result.status == true) {
      this.patientComments = result.data?.patient;
      this.synopticComments = result.data?.synoptic;
      this.synopticReports = result.data?.report;
      this.parsed = result.data?.parsed ? true : false;
    }
    this.contentLoaded = true;
  }

  closeModal() {
    this.activeModal.close([]);
  }
}