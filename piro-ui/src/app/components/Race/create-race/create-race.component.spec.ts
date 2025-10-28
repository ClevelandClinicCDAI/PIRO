import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateRaceComponent } from './create-race.component';

describe('CreateRaceComponent', () => {
  let component: CreateRaceComponent;
  let fixture: ComponentFixture<CreateRaceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateRaceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateRaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
