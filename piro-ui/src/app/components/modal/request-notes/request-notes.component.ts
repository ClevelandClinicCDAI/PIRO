import { Component, Input } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { DataService } from '../../../services/data.service';
import { ToastrService } from 'ngx-toastr';
import { RequesthistoryService } from 'src/app/services/requesthistory.service';


@Component({
  standalone: false,
  selector: 'app-request-notes',
  templateUrl: './request-notes.component.html',
  styleUrls: ['./request-notes.component.css']
})
export class RequestNotesComponent {

  contentLoaded = true;
  data: any = {"comment":  "", "approvalComment": "" };

  @Input() searchRequestId: number = -1;
  @Input() isdisabled: boolean = false;
  
  constructor(private activeModal: NgbActiveModal,         
    private requesthistoryService: RequesthistoryService,
    private toastr: ToastrService) {
     
  }

  async ngOnInit() {
    // console.log("isdisabled: ", this.isdisabled);
    this.getRequest();
  }

  async getRequest() {    
    this.contentLoaded = false;      
    const result : any = await this.requesthistoryService.getRequest(this.searchRequestId);
    if (result.status == true) {
      this.data = result.data;      
    } else {
      this.toastr.error('', 'Something went wrong.');
    }
    this.contentLoaded = true;
  }

  closeModal() {
    this.activeModal.close([]);
  }
  
  async saveComment() {
    this.contentLoaded = false;      
    const result : any = await this.requesthistoryService.updateComment(this.searchRequestId, this.data.approvalComment);
    if (result.status == true) {
      this.toastr.success('', 'Comment saved successfully');
      this.activeModal.close();
    } else {
      this.toastr.error('', 'Something went wrong.');
    }
    this.contentLoaded = true;
  }
}
