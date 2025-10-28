import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateSpecimenTypeComponent } from './create-specimen-type.component';

describe('CreateSpecimenTypeComponent', () => {
  let component: CreateSpecimenTypeComponent;
  let fixture: ComponentFixture<CreateSpecimenTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateSpecimenTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateSpecimenTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
