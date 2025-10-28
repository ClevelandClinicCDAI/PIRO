import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateSearchRequestStatusComponent } from './update-search-request-status.component';

describe('UpdateSearchRequestStatusComponent', () => {
  let component: UpdateSearchRequestStatusComponent;
  let fixture: ComponentFixture<UpdateSearchRequestStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateSearchRequestStatusComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateSearchRequestStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
