import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private data = new Subject<any>();
  public data$ = this.data.asObservable();

  constructor() { }

  emitdata(x: any){
    this.data.next(x);
  }

}
