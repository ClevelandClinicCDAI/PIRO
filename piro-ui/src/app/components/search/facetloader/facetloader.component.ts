import { Component, Input } from '@angular/core';

@Component({
  standalone: false,
  selector: 'app-facetloader',
  templateUrl: './facetloader.component.html',
  styleUrls: ['./facetloader.component.css']
})
export class FacetloaderComponent {
  @Input('contentLoaded') contentLoaded: any;
  @Input('value')  value: any;
}
