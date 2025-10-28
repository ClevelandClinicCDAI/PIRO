import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateEthnicityComponent } from './create-ethnicity.component';

describe('CreateEthnicityComponent', () => {
  let component: CreateEthnicityComponent;
  let fixture: ComponentFixture<CreateEthnicityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateEthnicityComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateEthnicityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
