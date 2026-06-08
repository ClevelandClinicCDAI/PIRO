import { Directive, ElementRef, Input } from '@angular/core';
import { SearchService } from '../services/search.service';

@Directive({
  standalone: false,
  selector: '[appTagDisplay]',
  providers: [SearchService]
})
export class TagDisplayDirective {
  @Input('caseid') caseId: any;
  constructor(private eleRef: ElementRef, private searchService: SearchService) { }

  ngAfterViewInit(): void {
    this.getTagsdata(this.caseId)
      .then((value) => {
        // console.log(value);
        // console.log("getTagsdata");
        this.eleRef.nativeElement.innerText = value;       
      });
  }

  async getTagsdata(caseId: number) {
    var tags = await this.searchService.getTags(caseId);
    return tags.data.join(', ');
  }

}
