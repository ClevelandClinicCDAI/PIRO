import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateSpecimenTypeComponent } from './update-specimen-type.component';

describe('UpdateSpecimenTypeComponent', () => {
  let component: UpdateSpecimenTypeComponent;
  let fixture: ComponentFixture<UpdateSpecimenTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateSpecimenTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateSpecimenTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
