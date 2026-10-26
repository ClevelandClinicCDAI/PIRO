import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultComponent } from './result.component';
import { ToastrService } from 'ngx-toastr';

describe('ResultComponent', () => {
  let component: ResultComponent;
  let fixture: ComponentFixture<ResultComponent>;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      declarations: [ ResultComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  afterEach(() => localStorage.clear());

  function result(caseid: number) {
    return {caseid: String(caseid), casenumber: `S26-${caseid}`, patientname: 'Synthetic patient',
      age: 40, gender: 'F', staffnames: [], interpreters: [], intraoptexts: []};
  }

  it('selects result cards across pages and searches and unchecks a returning case', () => {
    const info = spyOn(TestBed.inject(ToastrService), 'info');
    component.content = [result(1)]; component.count = 2; component.countLimit = 2;
    fixture.detectChanges();
    const checkbox = () => fixture.nativeElement.querySelector('input[type=checkbox]') as HTMLInputElement;
    checkbox().click(); fixture.detectChanges();
    expect(component.cart.has(1)).toBeTrue();
    expect(fixture.nativeElement.querySelector('.case-cart-toolbar').textContent).toContain('1 selected');
    component.content = [result(2)]; fixture.detectChanges(); checkbox().click(); fixture.detectChanges();
    expect(component.cart.count).toBe(2);
    component.content = []; fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.case-cart-toolbar button').disabled).toBeFalse();
    component.content = [result(1)]; fixture.detectChanges();
    expect(checkbox().checked).toBeTrue();
    checkbox().click(); fixture.detectChanges();
    expect(component.cart.has(1)).toBeFalse(); expect(component.cart.has(2)).toBeTrue();
    expect(fixture.nativeElement.textContent).not.toContain('Extraction Suite');
    expect(info).not.toHaveBeenCalled();
  });

  it('reports an invalid case separately from the cart limit', () => {
    const toastr = TestBed.inject(ToastrService);
    const info = spyOn(toastr, 'info'); const error = spyOn(toastr, 'error');
    const input = document.createElement('input'); input.type = 'checkbox'; input.checked = true;
    component.selectForCart({caseid: '', casenumber: 'Missing ID'}, {target: input} as unknown as Event);
    expect(input.checked).toBeFalse(); expect(info).not.toHaveBeenCalled();
    expect(error).toHaveBeenCalledWith(jasmine.stringMatching('identifier is missing or invalid'));
    expect(component.cart.count).toBe(0);
  });
});
