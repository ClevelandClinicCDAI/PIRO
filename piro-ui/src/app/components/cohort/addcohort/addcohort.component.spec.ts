import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddcohortComponent } from './addcohort.component';

describe('AddcohortComponent', () => {
  let component: AddcohortComponent;
  let fixture: ComponentFixture<AddcohortComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddcohortComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddcohortComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
