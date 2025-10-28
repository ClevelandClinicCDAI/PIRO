import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { EventTypes } from '../models/event-types';
import { ToastEvent } from '../models/toast-event';

@Injectable({
  providedIn: 'root',
})
export class ToastService {
  toastEvents: Observable<ToastEvent>;
  private _toastEvents = new Subject<ToastEvent>();

  constructor() {
    this.toastEvents = this._toastEvents.asObservable();
  }

  /**
   * Show success toast notification.
   * @param title Toast title
   * @param message Toast message
   */
  showSuccessToast(title: string, message: string,data:any) {
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.Success,
      data
    });
  }

  /**
   * Show info toast notification.
   * @param title Toast title
   * @param message Toast message
   */
  showInfoToast(title: string, message: string,data:any) {
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.Info,
      data
    });
  }

  /**
   * Show warning toast notification.
   * @param title Toast title
   * @param message Toast message
   */
  showWarningToast(title: string, message: string,data:any) {
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.Warning,
      data
    });
  }

  /**
   * Show error toast notification.
   * @param title Toast title
   * @param message Toast message
   */
  showErrorToast(title: string, message: string,data:any) {
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.Error,
      data
    });
  }

  showProgressToast(title: string, message: string,data:any){
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.Progress,
      data
    });
  }

  showDeleteErrorToast(title: string, message: string,data:any){
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.DeleteError,
      data
    });
  }
  showUploadErrorToast(title: string, message: string,data:any){
    this._toastEvents.next({
      message,
      title,
      type: EventTypes.UploadError,
      data
    });
  }
}