import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateRegionComponent } from './create-region.component';

describe('CreateRegionComponent', () => {
  let component: CreateRegionComponent;
  let fixture: ComponentFixture<CreateRegionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateRegionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateRegionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
