import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserattestComponent } from './userattest.component';

describe('UserattestComponent', () => {
  let component: UserattestComponent;
  let fixture: ComponentFixture<UserattestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserattestComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserattestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
