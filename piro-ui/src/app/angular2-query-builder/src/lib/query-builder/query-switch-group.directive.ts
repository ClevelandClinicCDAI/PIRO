import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[querySwitchGroup]'})
export class QuerySwitchGroupDirective {
  constructor(public template: TemplateRef<any>) {}
}
