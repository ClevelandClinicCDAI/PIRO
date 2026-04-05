import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { SlideRequest, SlideRequestCaseType, SlideRequestFormPayload } from '../models/slide-request';

@Injectable({
  providedIn: 'root'
})
export class SlideRequestService {
  private baseUrl = environment.apiBaseUrl + environment.slideRequestUrl;

  constructor(private http: HttpClient) { }

  private buildQueueOptions(caseType?: SlideRequestCaseType) {
    return caseType ? { params: { caseType } } : {};
  }

  createRequest(payload: SlideRequestFormPayload) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(this.baseUrl, payload).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  getMyRequests() {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(this.baseUrl).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getPendingRequests(caseType?: SlideRequestCaseType) {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/pending`, this.buildQueueOptions(caseType)).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getInProcessRequests(caseType?: SlideRequestCaseType) {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/in-process`, this.buildQueueOptions(caseType)).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getCompletedRequests(caseType?: SlideRequestCaseType) {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/completed`, this.buildQueueOptions(caseType)).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getHoldingRequests(caseType?: SlideRequestCaseType) {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/holding`, this.buildQueueOptions(caseType)).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  completeRequest(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/complete`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  takeRequest(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/in-process`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  holdRequest(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/hold`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  updateSlideRoomNotes(requestId: number, slideRoomNotes: string | null) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/notes`, { slideRoomNotes }).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  markNotInFile(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/nif`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  resetRequest(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/reset`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }

  cancelRequest(requestId: number) {
    return new Promise((resolve) => {
      this.http.post<SlideRequest>(`${this.baseUrl}/${requestId}/cancel`, {}).subscribe({
        next: (res: SlideRequest) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: null, err });
        }
      });
    });
  }
}
