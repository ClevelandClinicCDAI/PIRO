import { Component, HostListener } from '@angular/core';
import { Store } from '@ngrx/store';
import { SearchService } from '../../../services/search.service';

@Component({
  standalone: false,
  selector: 'app-autosuggest',
  templateUrl: './autosuggest.component.html',
  styleUrls: ['./autosuggest.component.css']
})
export class AutosuggestComponent {
  items:any = [];
  constructor(private searchService:SearchService,private store: Store<{ keyword: [] }>) { }
  ngOnInit(){
    this.store.select('keyword').subscribe( async (data:any)=>{
      if(data.keyword.content){
        const res = await this.searchService.getAutoSuggestData(data.keyword.content,data.keyword.type);
       if(res.status == true){
        this.items  = res.data;
       }
      }
    });
  }
  getValue(value:any){
    this.searchService.setStatusCount(true,value);
  }
  @HostListener('document:click', ['$event'])
  clickOut(event:any) {
      if (event.target.id != 'suggestions-container') 
      {
       this.searchService.setStatusCount(false,'');
      }
   }

}
