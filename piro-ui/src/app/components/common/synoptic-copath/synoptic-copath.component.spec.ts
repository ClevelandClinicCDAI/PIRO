import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SynopticCopathComponent } from './synoptic-copath.component';

describe('SynopticCopathComponent', () => {
  let component: SynopticCopathComponent;
  let fixture: ComponentFixture<SynopticCopathComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SynopticCopathComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SynopticCopathComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
