import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExportfieldComponent } from './exportfield.component';

describe('ExportfieldComponent', () => {
  let component: ExportfieldComponent;
  let fixture: ComponentFixture<ExportfieldComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExportfieldComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExportfieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
