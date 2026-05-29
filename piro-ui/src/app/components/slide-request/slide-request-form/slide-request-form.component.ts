import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SlideRequest, SlideRequestFormPayload, SlideRequestUrgency } from 'src/app/models/slide-request';
import { SlideRequestService } from 'src/app/services/slide-request.service';
import { ToastService } from 'src/app/services/toast.service';

@Component({
  selector: 'app-slide-request-form',
  templateUrl: './slide-request-form.component.html',
  styleUrls: ['./slide-request-form.component.css']
})
export class SlideRequestFormComponent implements OnInit {
  requestForm!: FormGroup;
  submitting = false;
  myRequests: SlideRequest[] = [];
  pendingMyRequests: SlideRequest[] = [];
  completedMyRequests: SlideRequest[] = [];
  canceling: { [key: number]: boolean } = {};
  errorMessage = '';
  urgencyOptions: { value: SlideRequestUrgency; label: string }[] = [
    { value: 'SameDay', label: 'Same Day' },
    { value: 'Routine', label: 'Routine' }
  ];

  constructor(
    private formBuilder: FormBuilder,
    private slideRequestService: SlideRequestService,
    private toastService: ToastService
  ) {}

  async ngOnInit() {
    this.requestForm = this.formBuilder.group({
      accessionNumber: ['', [Validators.required, Validators.maxLength(500)]],
      requesterNotes: ['', [Validators.maxLength(2000)]],
      ePath: [false],
      urgencyStatus: ['Routine', [Validators.required]]
    });
    await this.loadMyRequests();
  }

  get f() {
    return this.requestForm.controls;
  }

  async onSubmit() {
    this.submitting = true;
    this.errorMessage = '';
    if (this.requestForm.invalid) {
      this.submitting = false;
      this.errorMessage = 'Please correct the errors and try again.';
      return;
    }

    const payloads = this.buildPayloads();
    if (payloads.length > 25) {
      this.submitting = false;
      this.errorMessage = 'You may submit a maximum of 25 cases at a time.';
      return;
    }
    const results: { payload: SlideRequestFormPayload; result: any }[] = await Promise.all(
      payloads.map(async (payload) => {
        const result = await this.slideRequestService.createRequest(payload);
        return { payload, result };
      })
    );
    this.submitting = false;

    const failed = results.filter((item) => !item.result?.status);
    const succeeded = results.filter((item) => item.result?.status).map((item) => item.result?.data);
    if (failed.length > 0) {
      const codes = failed.map((item) => item.payload.accessionNumber).join(', ');
      this.errorMessage = `Unable to submit request${failed.length > 1 ? 's' : ''} for: ${codes}`;
    }
    if (succeeded.length > 0) {
      const successTitle = succeeded.length === 1 ? 'Slide requested' : 'Slides requested';
      this.toastService.showSuccessToast(successTitle, 'Your request has been submitted to the slide room queue.', []);
      this.myRequests = [...succeeded, ...this.myRequests];
      this.splitRequests();
    }

    this.requestForm.reset({
      accessionNumber: '',
      urgencyStatus: 'Routine',
      requesterNotes: '',
      ePath: false
    });
  }

  private buildPayloads(): SlideRequestFormPayload[] {
    const accessionRaw = (this.requestForm.value.accessionNumber as string) || '';
    const caseNumbers = accessionRaw
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
    const urgencyStatus = this.requestForm.value.urgencyStatus as SlideRequestUrgency;
    const requesterNotes = (this.requestForm.value.requesterNotes as string)?.trim();
    const ePath = Boolean(this.requestForm.value.ePath);

    return caseNumbers.map((accessionNumber) => ({
      accessionNumber,
      urgencyStatus,
      requesterNotes,
      ePath
    }));
  }

  async loadMyRequests() {
    this.errorMessage = '';
    const result: any = await this.slideRequestService.getMyRequests();
    if (result?.status) {
      this.myRequests = result.data || [];
      this.splitRequests();
    } else {
      this.errorMessage = 'Unable to load your slide requests.';
    }
  }

  async cancelRequest(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    this.canceling[request.id] = true;
    const result: any = await this.slideRequestService.cancelRequest(request.id);
    this.canceling[request.id] = false;
    if (result?.status && result.data) {
      this.toastService.showInfoToast('Request canceled', 'The slide request was canceled.', []);
      this.myRequests = this.myRequests.map((item) => (item.id === request.id ? result.data : item));
      this.splitRequests();
    } else {
      this.toastService.showErrorToast('Unable to cancel', 'Please try again.', []);
    }
  }

  trackById(index: number, item: SlideRequest) {
    return item.id || index;
  }

  getUrgencyLabel(urgency: SlideRequestUrgency | undefined) {
    if (urgency === 'SameDay') {
      return 'Same Day';
    }
    if (urgency === 'Routine') {
      return 'Routine';
    }
    return 'Unknown';
  }

  getUrgencyBadgeClasses(urgency: SlideRequestUrgency | undefined) {
    if (urgency === 'SameDay') {
      return 'badge rounded-pill bg-danger urgency-badge';
    }
    if (urgency === 'Routine') {
      return 'badge rounded-pill bg-secondary';
    }
    return 'badge rounded-pill bg-light text-dark border';
  }

  getStatusLabel(status: string | undefined | null) {
    if (status === 'CANCELED') {
      return 'Canceled';
    }
    return status || '-';
  }

  private splitRequests() {
    this.pendingMyRequests = this.myRequests.filter((item) => this.isPendingStatus(item.status));
    this.completedMyRequests = this.myRequests.filter((item) => !this.isPendingStatus(item.status));
  }

  private isPendingStatus(status: string | undefined | null) {
    return status === 'PENDING' || status === 'IN_PROCESS' || status === 'HOLDING';
  }
}
