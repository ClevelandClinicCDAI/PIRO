import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvancedsearchmodalComponent } from './advancedsearchmodal.component';

describe('AdvancedsearchmodalComponent', () => {
  let component: AdvancedsearchmodalComponent;
  let fixture: ComponentFixture<AdvancedsearchmodalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdvancedsearchmodalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdvancedsearchmodalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
