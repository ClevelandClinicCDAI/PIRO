import { Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { loadFacets, loadResult } from 'src/app/store/result.actions';

import { SearchService } from '../../../services/search.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent {
  constructor( private readonly store: Store, private searchService:SearchService){}

  ngOnInit(){
   // this.store.dispatch(ResultActions.loadResultsResultss());
  }

  

  
  
}
