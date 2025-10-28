import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListSearchRequestStatusComponent } from './list-search-request-status.component';

describe('ListSearchRequestStatusComponent', () => {
  let component: ListSearchRequestStatusComponent;
  let fixture: ComponentFixture<ListSearchRequestStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListSearchRequestStatusComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListSearchRequestStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
