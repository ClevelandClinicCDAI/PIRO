import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-aireviewcasedetail',
  templateUrl: './aireviewcasedetail.component.html',
  styleUrls: ['./aireviewcasedetail.component.css']
})
export class AireviewcasedetailComponent {
  @Input() public caseIdInput: number = 0;
  @Input() public caseNum: string = '';

  constructor(private activeModal: NgbActiveModal) {

  }
  closeModal(){
    this.activeModal.close('Modal Closed');
  }
}
