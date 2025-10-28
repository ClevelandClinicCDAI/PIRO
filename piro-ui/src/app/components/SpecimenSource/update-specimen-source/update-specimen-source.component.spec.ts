import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateSpecimenSourceComponent } from './update-specimen-source.component';

describe('UpdateSpecimenSourceComponent', () => {
  let component: UpdateSpecimenSourceComponent;
  let fixture: ComponentFixture<UpdateSpecimenSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateSpecimenSourceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateSpecimenSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
