import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryOperator]'})
export class QueryOperatorDirective {
  constructor(public template: TemplateRef<any>) {}
}
