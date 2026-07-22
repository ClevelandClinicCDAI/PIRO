import { Directive, ElementRef, Input } from '@angular/core';

@Directive({
  standalone: false,
  selector: '[appCommentDisplay]'
})
export class CommentDisplayDirective {
  //@Input('selectable') option:any;   
  @Input('heading') heading:any;
  @Input('comment') comment:any;
  @Input('appCommentDisplay') initialData: any;
  constructor(private eleRef: ElementRef) {
   
   }

   ngAfterViewInit(): void {
    // this.eleRef.nativeElement.innerHTML = "<b class='result-heading'>"+this.initialData.heading+"</b><br>\
    // <div class='paragraph' [ngFor]='let fin of this.initialData.content'>\
    //     <p class='result-comment'>"+{{fin}}+"</p>\
    // </div>";
    
    this.eleRef.nativeElement.children[0].innerHTML = this.comment;
 }
}
