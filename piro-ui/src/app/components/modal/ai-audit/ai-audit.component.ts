import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { AivoteService } from '../../../services/aivote.service';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-ai-audit',
  templateUrl: './ai-audit.component.html',
  styleUrls: ['./ai-audit.component.css']
})
export class AiAuditComponent {
	@Input() public caseid: number = 0;
	@Input() public annotationConfigurationId: number = 0;
	@Input() public annotationName: string = '';
	@Input() public casenum: string = '';

	loaded: boolean = true;
	items: any = [];
	constructor(private activeModal: NgbActiveModal,
		private aiVoteService: AivoteService,private toastr: ToastrService,private confirmDialogService: ConfirmDialogService) {
	}

	async ngOnInit() {
		this.getAll();
	}

	async getAll() {
		this.loaded = false;
		var data = {
			"caseid": this.caseid,
			"configid": this.annotationConfigurationId		 
		}
		const result: any = await this.aiVoteService.getAudit(data);
		if (result.status == true) {
			this.items = result.data;
			this.loaded = true;
		}
	}

	closeModal() {
		this.activeModal.close(true);
	}
 
} 
