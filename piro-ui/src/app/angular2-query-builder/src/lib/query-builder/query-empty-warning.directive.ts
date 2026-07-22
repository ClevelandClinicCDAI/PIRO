import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryEmptyWarning]'})
export class QueryEmptyWarningDirective {
  constructor(public template: TemplateRef<any>) {}
}
