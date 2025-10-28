import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestNotesComponent } from './request-notes.component';

describe('RequestNotesComponent', () => {
  let component: RequestNotesComponent;
  let fixture: ComponentFixture<RequestNotesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RequestNotesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RequestNotesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
