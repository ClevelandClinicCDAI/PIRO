import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExtractRequestComponent } from './extract-request.component';

describe('ExtractRequestComponent', () => {
  let component: ExtractRequestComponent;
  let fixture: ComponentFixture<ExtractRequestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExtractRequestComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExtractRequestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
