import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { AivoteService } from '../../../services/aivote.service';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
import { ToastrService } from 'ngx-toastr';

@Component({
	selector: 'app-aireview',
	templateUrl: './aireview.component.html',
	styleUrls: ['./aireview.component.css']
})
export class AireviewComponent {
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
			"annotationConfigurationId": this.annotationConfigurationId,
			"casenum": '',
			pending: false,
			feedback: 0
		}
		const result: any = await this.aiVoteService.getAIVoteReviews(data);
		if (result.status == true) {
			this.items = result.data;
			this.loaded = true;
		}
	}

	closeModal() {
		this.activeModal.close(true);
	}

	reviewFeedback(annotationCaseFeedbackId: number) {
		let that = this;
		this.confirmDialogService.confirmThis("Are you sure to close the review?", async function () {
		const result: any = await that.aiVoteService.markReviewed(annotationCaseFeedbackId);
		if (result.status == true) {
			that.getAll();
		} else {
			that.toastr.error('', 'Something went wrong.');
		}
		}, function () {

		});
	}
}
