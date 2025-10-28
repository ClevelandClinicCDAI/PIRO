import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListRaceComponent } from './list-race.component';

describe('ListRaceComponent', () => {
  let component: ListRaceComponent;
  let fixture: ComponentFixture<ListRaceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListRaceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListRaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
