import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryArrowIcon]'})
export class QueryArrowIconDirective {
  constructor(public template: TemplateRef<any>) {}
}
