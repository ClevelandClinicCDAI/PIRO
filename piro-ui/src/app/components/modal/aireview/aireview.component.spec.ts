import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AireviewComponent } from './aireview.component';

describe('AireviewComponent', () => {
  let component: AireviewComponent;
  let fixture: ComponentFixture<AireviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AireviewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AireviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
