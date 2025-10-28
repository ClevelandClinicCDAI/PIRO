import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavedsearchcontentmodalComponent } from './savedsearchcontentmodal.component';

describe('SavedsearchcontentmodalComponent', () => {
  let component: SavedsearchcontentmodalComponent;
  let fixture: ComponentFixture<SavedsearchcontentmodalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SavedsearchcontentmodalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SavedsearchcontentmodalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
