import { Directive, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryRemoveButton]'})
export class QueryRemoveButtonDirective {
  constructor(public template: TemplateRef<any>) {}
}
