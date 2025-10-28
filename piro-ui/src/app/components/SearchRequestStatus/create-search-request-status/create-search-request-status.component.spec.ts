import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateSearchRequestStatusComponent } from './create-search-request-status.component';

describe('CreateSearchRequestStatusComponent', () => {
  let component: CreateSearchRequestStatusComponent;
  let fixture: ComponentFixture<CreateSearchRequestStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateSearchRequestStatusComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateSearchRequestStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
