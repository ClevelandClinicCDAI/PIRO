import { Directive, Input, TemplateRef } from '@angular/core';

@Directive({standalone: false, selector: '[queryInput]'})
export class QueryInputDirective {
  private _type: string;
  /** Unique name for query input type. */
  @Input()
  get queryInputType(): string { return this._type; }
  set queryInputType(value: string) {
    // If the directive is set without a type (updated programatically), then this setter will
    // trigger with an empty string and should not overwrite the programatically set value.
    if (!value) { return; }
    this._type = value;
  }
 

  constructor(public template: TemplateRef<any>) {
    
  }
}
