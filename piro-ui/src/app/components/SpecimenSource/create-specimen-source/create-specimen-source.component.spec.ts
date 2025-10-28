import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateSpecimenSourceComponent } from './create-specimen-source.component';

describe('CreateSpecimenSourceComponent', () => {
  let component: CreateSpecimenSourceComponent;
  let fixture: ComponentFixture<CreateSpecimenSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateSpecimenSourceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateSpecimenSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
