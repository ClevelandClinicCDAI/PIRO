import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateGenderComponent } from './update-gender.component';

describe('UpdateGenderComponent', () => {
  let component: UpdateGenderComponent;
  let fixture: ComponentFixture<UpdateGenderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateGenderComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateGenderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
