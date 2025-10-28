import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewsearchComponent } from './viewsearch.component';

describe('ViewsearchComponent', () => {
  let component: ViewsearchComponent;
  let fixture: ComponentFixture<ViewsearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ViewsearchComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewsearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
