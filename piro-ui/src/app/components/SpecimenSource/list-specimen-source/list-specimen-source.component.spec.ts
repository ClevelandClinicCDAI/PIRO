import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListSpecimenSourceComponent } from './list-specimen-source.component';

describe('ListSpecimenSourceComponent', () => {
  let component: ListSpecimenSourceComponent;
  let fixture: ComponentFixture<ListSpecimenSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListSpecimenSourceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListSpecimenSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
