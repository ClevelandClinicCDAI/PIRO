import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AireviewcasedetailComponent } from './aireviewcasedetail.component';

describe('AireviewcasedetailComponent', () => {
  let component: AireviewcasedetailComponent;
  let fixture: ComponentFixture<AireviewcasedetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AireviewcasedetailComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AireviewcasedetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
