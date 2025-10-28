import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavesearchmodalComponent } from './savesearchmodal.component';

describe('SavesearchmodalComponent', () => {
  let component: SavesearchmodalComponent;
  let fixture: ComponentFixture<SavesearchmodalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SavesearchmodalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SavesearchmodalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
