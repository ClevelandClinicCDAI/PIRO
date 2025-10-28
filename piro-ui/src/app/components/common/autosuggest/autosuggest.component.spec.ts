import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutosuggestComponent } from './autosuggest.component';

describe('AutosuggestComponent', () => {
  let component: AutosuggestComponent;
  let fixture: ComponentFixture<AutosuggestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AutosuggestComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AutosuggestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
