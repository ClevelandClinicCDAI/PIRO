import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AireviewsComponent } from './aireviews.component';

describe('AireviewsComponent', () => {
  let component: AireviewsComponent;
  let fixture: ComponentFixture<AireviewsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AireviewsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AireviewsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
