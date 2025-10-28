import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListEthnicityComponent } from './list-ethnicity.component';

describe('ListEthnicityComponent', () => {
  let component: ListEthnicityComponent;
  let fixture: ComponentFixture<ListEthnicityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListEthnicityComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListEthnicityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
