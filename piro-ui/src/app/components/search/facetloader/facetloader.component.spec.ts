import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FacetloaderComponent } from './facetloader.component';

describe('FacetloaderComponent', () => {
  let component: FacetloaderComponent;
  let fixture: ComponentFixture<FacetloaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FacetloaderComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FacetloaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
