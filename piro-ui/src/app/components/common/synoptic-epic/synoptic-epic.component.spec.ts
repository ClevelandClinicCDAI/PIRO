import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SynopticEpicComponent } from './synoptic-epic.component';

describe('SynopticEpicComponent', () => {
  let component: SynopticEpicComponent;
  let fixture: ComponentFixture<SynopticEpicComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SynopticEpicComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SynopticEpicComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
