import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateRaceComponent } from './update-race.component';

describe('UpdateRaceComponent', () => {
  let component: UpdateRaceComponent;
  let fixture: ComponentFixture<UpdateRaceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateRaceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateRaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
