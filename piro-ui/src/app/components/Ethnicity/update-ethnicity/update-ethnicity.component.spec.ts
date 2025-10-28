import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateEthnicityComponent } from './update-ethnicity.component';

describe('UpdateEthnicityComponent', () => {
  let component: UpdateEthnicityComponent;
  let fixture: ComponentFixture<UpdateEthnicityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateEthnicityComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateEthnicityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
