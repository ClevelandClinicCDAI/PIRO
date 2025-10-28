import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditcohortComponent } from './editcohort.component';

describe('EditcohortComponent', () => {
  let component: EditcohortComponent;
  let fixture: ComponentFixture<EditcohortComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditcohortComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditcohortComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
