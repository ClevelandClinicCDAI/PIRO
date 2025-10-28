import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListSepcimentTypeComponent } from './list-sepciment-type.component';

describe('ListSepcimentTypeComponent', () => {
  let component: ListSepcimentTypeComponent;
  let fixture: ComponentFixture<ListSepcimentTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListSepcimentTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListSepcimentTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
