import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreategenderComponent } from './creategender.component';

describe('CreategenderComponent', () => {
  let component: CreategenderComponent;
  let fixture: ComponentFixture<CreategenderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreategenderComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreategenderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
