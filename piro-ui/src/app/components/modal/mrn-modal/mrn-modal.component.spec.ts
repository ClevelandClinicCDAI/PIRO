import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MrnModalComponent } from './mrn-modal.component';

describe('MrnModalComponent', () => {
  let component: MrnModalComponent;
  let fixture: ComponentFixture<MrnModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MrnModalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MrnModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
