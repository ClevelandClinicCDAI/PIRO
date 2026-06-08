import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryEntity]'})
export class QueryEntityDirective {
  constructor(public template: TemplateRef<any>) {}
}
