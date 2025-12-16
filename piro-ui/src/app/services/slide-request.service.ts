import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { SlideRequest, SlideRequestFormPayload } from '../models/slide-request';

@Injectable({
  providedIn: 'root'
})
export class SlideRequestService {
  private baseUrl = environment.apiBaseUrl + environment.slideRequestUrl;

  constructor(private http: HttpClient) { }

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

  getPendingRequests() {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/pending`).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getInProcessRequests() {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/in-process`).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getCompletedRequests() {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/completed`).subscribe({
        next: (res: SlideRequest[]) => {
          resolve({ status: true, data: res });
        },
        error: (err: any) => {
          resolve({ status: false, data: [], err });
        }
      });
    });
  }

  getHoldingRequests() {
    return new Promise((resolve) => {
      this.http.get<SlideRequest[]>(`${this.baseUrl}/holding`).subscribe({
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
}
