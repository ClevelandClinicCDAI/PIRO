import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateHospitalComponent } from './create-hospital.component';

describe('CreateHospitalComponent', () => {
  let component: CreateHospitalComponent;
  let fixture: ComponentFixture<CreateHospitalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateHospitalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateHospitalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
