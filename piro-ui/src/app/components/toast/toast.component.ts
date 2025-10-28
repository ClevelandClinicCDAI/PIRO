/* eslint-disable @typescript-eslint/no-unsafe-argument */
import { Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { Toast } from 'bootstrap';
import { fromEvent, take } from 'rxjs';
import { EventTypes } from '../../models/event-types';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css'],
})
export class ToastComponent implements OnInit {
  @Output() disposeEvent = new EventEmitter();

  @ViewChild('toastElement', { static: true })
  toastEl!: ElementRef;

  @Input()
  type!: EventTypes;

  @Input()
  title!: string;

  @Input()
  message!: string;

  @Input()
  data!: any;

  toast!: Toast;

  constructor() {

  }

  ngOnInit() {
    this.show();
  }
  
  show() {
    const errorTypes = [EventTypes.Error,EventTypes.DeleteError,EventTypes.UploadError];
    this.toast = new Toast(
      this.toastEl.nativeElement,
      errorTypes.includes(this.type) 
      ? { 
          autohide: true,
          delay:3000  
        } 
      : 
      { 
          autohide: true, 
          delay:3000 
      }
    );

    fromEvent(this.toastEl.nativeElement, 'hidden.bs.toast')
      .pipe(take(1))
      .subscribe(() => this.hide());

    this.toast.show();
  }

  hide() {
    this.toast.dispose();
    this.disposeEvent.emit();
  }
  
}