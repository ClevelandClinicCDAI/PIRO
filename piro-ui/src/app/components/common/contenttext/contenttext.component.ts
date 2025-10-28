import { Component, Input, ViewEncapsulation } from '@angular/core';
import { EMFJS, RTFJS, WMFJS } from 'rtf.js';
@Component({
  selector: '[app-contenttext]',
  templateUrl: './contenttext.component.html',
  styleUrls: ['./contenttext.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class ContenttextComponent {
  @Input('app-contenttext') inData: any;
  ngOnInit(): void {

  }  
}
