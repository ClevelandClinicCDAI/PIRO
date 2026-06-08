import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryField]'})
export class QueryFieldDirective {
  constructor(public template: TemplateRef<any>) {}
}
