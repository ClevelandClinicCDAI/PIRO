import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryButtonGroup]'})
export class QueryButtonGroupDirective {
  constructor(public template: TemplateRef<any>) {}
}
