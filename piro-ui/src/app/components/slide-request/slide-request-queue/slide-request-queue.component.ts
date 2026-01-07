import { Component, OnInit, OnDestroy } from '@angular/core';
import { SlideRequest, SlideRequestUrgency } from 'src/app/models/slide-request';
import { SlideRequestService } from 'src/app/services/slide-request.service';
import { ToastService } from 'src/app/services/toast.service';

@Component({
  selector: 'app-slide-request-queue',
  templateUrl: './slide-request-queue.component.html',
  styleUrls: ['./slide-request-queue.component.css']
})
export class SlideRequestQueueComponent implements OnInit, OnDestroy {
  pendingRequests: SlideRequest[] = [];
  inProcessRequests: SlideRequest[] = [];
  holdingRequests: SlideRequest[] = [];
  completedRequests: SlideRequest[] = [];
  isLoadingPending = false;
  isLoadingInProcess = false;
  isLoadingHolding = false;
  isLoadingCompleted = false;
  updating: { [key: number]: boolean } = {};
  savingNotes: { [key: number]: boolean } = {};
  editingNotes: { [key: number]: string } = {};
  errorMessage = '';
  inProcessErrorMessage = '';
  holdingErrorMessage = '';
  completedErrorMessage = '';
  urgencyLabels: Record<SlideRequestUrgency, string> = {
    SameDay: 'Same Day',
    Routine: 'Routine'
  };
  private refreshTimer: any;
  private readonly refreshIntervalMs = 15000;

  constructor(
    private slideRequestService: SlideRequestService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.loadRequests();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  async loadRequests() {
    this.isLoadingPending = true;
    this.isLoadingInProcess = true;
    this.isLoadingHolding = true;
    this.isLoadingCompleted = true;
    this.errorMessage = '';
    this.inProcessErrorMessage = '';
    this.holdingErrorMessage = '';
    this.completedErrorMessage = '';

    const [pendingResult, inProcessResult, holdingResult, completedResult]: any = await Promise.all([
      this.slideRequestService.getPendingRequests(),
      this.slideRequestService.getInProcessRequests(),
      this.slideRequestService.getHoldingRequests(),
      this.slideRequestService.getCompletedRequests()
    ]);

    this.isLoadingPending = false;
    this.isLoadingInProcess = false;
    this.isLoadingHolding = false;
    this.isLoadingCompleted = false;

    if (pendingResult?.status) {
      this.pendingRequests = pendingResult.data || [];
    } else {
      this.errorMessage = 'Unable to load the slide request queue.';
    }

    if (inProcessResult?.status) {
      this.inProcessRequests = inProcessResult.data || [];
    } else {
      this.inProcessErrorMessage = 'Unable to load in-process slide requests.';
    }

    if (holdingResult?.status) {
      this.holdingRequests = holdingResult.data || [];
    } else {
      this.holdingErrorMessage = 'Unable to load holding slide requests.';
    }

    if (completedResult?.status) {
      this.completedRequests = completedResult.data || [];
    } else {
      this.completedErrorMessage = 'Unable to load completed slide requests.';
    }
  }

  async markCompleted(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    this.updating[request.id] = true;
    const result: any = await this.slideRequestService.completeRequest(request.id);
    this.updating[request.id] = false;
    if (result?.status) {
      this.toastService.showSuccessToast('Request completed', 'The slide request was closed.', []);
      this.pendingRequests = this.pendingRequests.filter((item) => item.id !== request.id);
      this.inProcessRequests = this.inProcessRequests.filter((item) => item.id !== request.id);
      this.holdingRequests = this.holdingRequests.filter((item) => item.id !== request.id);
      delete this.editingNotes[request.id];
      delete this.savingNotes[request.id];
      if (result.data) {
        this.completedRequests = [result.data, ...this.completedRequests];
      }
    } else {
      this.toastService.showErrorToast('Unable to complete', 'Please try marking the request as done again.', []);
    }
  }

  async markNotInFile(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    this.updating[request.id] = true;
    const result: any = await this.slideRequestService.markNotInFile(request.id);
    this.updating[request.id] = false;
    if (result?.status) {
      this.toastService.showInfoToast('Marked NIF', 'Slides not found in file.', []);
      this.pendingRequests = this.pendingRequests.filter((item) => item.id !== request.id);
      this.inProcessRequests = this.inProcessRequests.filter((item) => item.id !== request.id);
      this.holdingRequests = this.holdingRequests.filter((item) => item.id !== request.id);
      delete this.editingNotes[request.id];
      delete this.savingNotes[request.id];
      if (result.data) {
        this.completedRequests = [result.data, ...this.completedRequests];
      }
    } else {
      this.toastService.showErrorToast('Unable to update', 'Please try marking as NIF again.', []);
    }
  }

  async moveToHolding(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    this.updating[request.id] = true;
    const result: any = await this.slideRequestService.holdRequest(request.id);
    this.updating[request.id] = false;
    if (result?.status) {
      this.toastService.showInfoToast('Moved to Holding', 'The request was placed in the holding queue.', []);
      this.pendingRequests = this.pendingRequests.filter((item) => item.id !== request.id);
      this.inProcessRequests = this.inProcessRequests.filter((item) => item.id !== request.id);
      delete this.editingNotes[request.id];
      delete this.savingNotes[request.id];
      if (result.data) {
        this.holdingRequests = [result.data, ...this.holdingRequests];
      }
    } else {
      this.toastService.showErrorToast('Unable to hold request', 'Please try moving to holding again.', []);
    }
  }

  async markInProcess(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    this.updating[request.id] = true;
    const result: any = await this.slideRequestService.takeRequest(request.id);
    this.updating[request.id] = false;
    if (result?.status) {
      this.toastService.showSuccessToast('Request taken', 'The request is now marked as In Process.', []);
      this.pendingRequests = this.pendingRequests.filter((item) => item.id !== request.id);
      this.holdingRequests = this.holdingRequests.filter((item) => item.id !== request.id);
      delete this.editingNotes[request.id];
      delete this.savingNotes[request.id];
      if (result.data) {
        this.inProcessRequests = [result.data, ...this.inProcessRequests];
      }
    } else {
      this.toastService.showErrorToast('Unable to take request', 'Please try again.', []);
    }
  }

  trackById(index: number, item: SlideRequest) {
    return item.id || index;
  }

  getUrgencyLabel(urgency: SlideRequestUrgency | undefined) {
    if (urgency && this.urgencyLabels[urgency]) {
      return this.urgencyLabels[urgency];
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

  startEditingNotes(request: SlideRequest) {
    this.editingNotes[request.id] = request.slideRoomNotes || '';
  }

  cancelEditingNotes(requestId: number) {
    delete this.editingNotes[requestId];
  }

  isEditingNotes(requestId: number) {
    return this.editingNotes[requestId] !== undefined;
  }

  async saveSlideRoomNotes(request: SlideRequest) {
    if (!request?.id) {
      return;
    }
    const noteText = (this.editingNotes[request.id] || '').trim();
    this.savingNotes[request.id] = true;
    const result: any = await this.slideRequestService.updateSlideRoomNotes(request.id, noteText || null);
    this.savingNotes[request.id] = false;
    if (result?.status && result.data) {
      this.toastService.showSuccessToast('Notes updated', 'Slide room notes were saved.', []);
      this.replaceRequestInQueues(result.data);
      delete this.editingNotes[request.id];
    } else {
      this.toastService.showErrorToast('Unable to save notes', 'Please try again.', []);
    }
  }

  private replaceRequestInQueues(updated: SlideRequest) {
    this.pendingRequests = this.pendingRequests.map((item) => (item.id === updated.id ? updated : item));
    this.inProcessRequests = this.inProcessRequests.map((item) => (item.id === updated.id ? updated : item));
    this.holdingRequests = this.holdingRequests.map((item) => (item.id === updated.id ? updated : item));
    this.completedRequests = this.completedRequests.map((item) => (item.id === updated.id ? updated : item));
  }

  private startAutoRefresh() {
    this.stopAutoRefresh();
    this.refreshTimer = setInterval(() => {
      this.loadRequests();
    }, this.refreshIntervalMs);
  }

  private stopAutoRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }
}
