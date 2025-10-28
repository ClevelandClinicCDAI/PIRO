import { Component, Injector, Input } from '@angular/core';
import { SearchService } from '../../../services/search.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-synoptic-copath',
  templateUrl: './synoptic-copath.component.html',
  styleUrls: ['./synoptic-copath.component.css']
})
export class SynopticCopathComponent {
  coPathSynopticComments: any = [];
  contentLoaded = false;
  activeModal!: NgbActiveModal;

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
    const result = await this.searchService.getCoPathComments(+this.caseId);
    if (result.status == true) {
      this.coPathSynopticComments = result.data.filter((item: any) => item.type == 'Synoptic');
    }
    this.contentLoaded = true;
  }

  closeModal() {
    this.activeModal.close([]);
  }
}
