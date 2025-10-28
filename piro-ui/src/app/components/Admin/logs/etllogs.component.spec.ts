import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EtllogsComponent } from './etllogs.component';

describe('EtllogsComponent', () => {
  let component: EtllogsComponent;
  let fixture: ComponentFixture<EtllogsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EtllogsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EtllogsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
