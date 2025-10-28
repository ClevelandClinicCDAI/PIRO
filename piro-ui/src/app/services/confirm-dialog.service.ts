import { Injectable } from '@angular/core';
//import { Router, NavigationStart } from '@angular/router';  
import { Observable } from 'rxjs';
import { Subject } from 'rxjs';

@Injectable() export class ConfirmDialogService {
  private subject = new Subject<any>();

  confirmThis(message: string, yesFn: () => void, noFn: () => void): any {
  
    this.setConfirmation(message, 'custom-alert', yesFn, noFn);
  }

  confirmClassThis(message: string, classname: string, yesFn: () => void, noFn: () => void): any {
  
    this.setConfirmation(message, classname, yesFn, noFn);
  }


  confirmCustom(message: string, classname: string, yesText: string, noText: string, yesFn: () => void, noFn: () => void): any {
    const that = this;
    this.subject.next({
      type: 'confirm',
      text: message,
      yestext: yesText,
      notext: noText,
      classname: classname == '' ? 'custom-alert' : classname,
      isalert: false,
      yesFn(): any {
        that.subject.next(0); // This will close the modal  
        yesFn();
      },
      noFn(): any {
        that.subject.next(0);
        noFn();
      }
    });
  }

  alertCustom(message: string, classname: string, yesText: string, yesFn: () => void): any {
    const that = this;
    this.subject.next({
      type: 'confirm',
      text: message,
      yestext: yesText,
      isalert: true,
      classname: classname == '' ? 'custom-alert' : classname,
      yesFn(): any {
        that.subject.next(0); // This will close the modal  
        yesFn();
      }
    });
  }

  setConfirmation(message: string, classname: string, yesFn: () => void, noFn: () => void): any {
    const that = this;
    this.subject.next({
      type: 'confirm',
      text: message,
      yestext: 'YES',
      notext: 'NO',
      classname: classname,
      isalert: false,
      yesFn(): any {
        that.subject.next(0); // This will close the modal  
        yesFn();
      },
      noFn(): any {
        that.subject.next(0);
        noFn();
      }
    });
  }

  getMessage(): Observable<any> {
    return this.subject.asObservable();
  }
}  
