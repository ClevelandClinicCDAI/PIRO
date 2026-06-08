import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { AivoteService } from '../../../services/aivote.service';

@Component({
  standalone: false,
	selector: 'app-ai-vote',
	templateUrl: './ai-vote.component.html',
	styleUrls: ['./ai-vote.component.css']
})
export class AiVoteComponent {
	@Input() public caseid: number = 0;
	@Input() public casenum: string = '';
	@Input() public annotationConfigurationId: number = 0;
	@Input() public vote: number = 0;
	@Input() public annotationName: string = '';
	@Input() public annotationText: string = '';

	submitted: boolean = false;
	description: string = '---'
	saveAIForm: any = FormGroup;

	iscommentrequiredApprove: boolean = false;
	iscommentrequiredReject: boolean = false;

	constructor(private activeModal: NgbActiveModal,
		private formBuilder: FormBuilder,
		private aiVoteService: AivoteService,
		private toastr: ToastrService,
		private router: Router) {
	}

	async ngOnInit() {
		if (this.vote == -1) {
			this.description = `<span  class="btn btn-secondary position-relative"><i class="bi bi-x-square"></i></span> You are rejecting the annotation <b><i><u>${this.annotationName} </b></u></i>. Please specify the reason and save`;
			this.saveAIForm = this.formBuilder.group({
				comment: this.iscommentrequiredReject ? ['',  [Validators.required]] : [''],
				feedback: [this.vote],
				caseid:this.caseid,
				annotationConfigurationId:this.annotationConfigurationId
			});

		} else if (this.vote == 1) {
			this.description = `<span class="btn btn-primary position-relative"><i class="bi bi-check-square"></i></span> You are approving the annotation <b><i><u>${this.annotationName} </b></u></i>. Please save`;
			this.saveAIForm = this.formBuilder.group({
				comment: this.iscommentrequiredApprove ? ['',  [Validators.required]] : [''],
				feedback: [this.vote],
				caseid:this.caseid,
				annotationConfigurationId:this.annotationConfigurationId
			});
		}
	}

	get f() { return this.saveAIForm.controls; }


	async submitForm() {
		this.submitted = true;
		// stop here if form is invalid
		if (this.saveAIForm.invalid) {
			return;
		}

		//True if all the fields are filled
		if (this.submitted) {
			const res: any = await this.aiVoteService.saveVote(this.saveAIForm.value);
			if (res.status == true) {
				this.toastr.success('', 'Feedback Submitted successfully.');
				this.activeModal.close('Modal Closed');
			} else if (res.status == false) {
				this.toastr.error('', res.err);
			} else {
				this.toastr.error('', 'Something went wrong.');
			}
		}
	}



	closeModal() {
		this.activeModal.close('Modal Closed');
	}
}
