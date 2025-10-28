import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateRegionComponent } from './update-region.component';

describe('UpdateRegionComponent', () => {
  let component: UpdateRegionComponent;
  let fixture: ComponentFixture<UpdateRegionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateRegionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateRegionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
