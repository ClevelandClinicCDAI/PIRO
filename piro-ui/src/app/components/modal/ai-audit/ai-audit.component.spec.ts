import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AiAuditComponent } from './ai-audit.component';

describe('AiAuditComponent', () => {
  let component: AiAuditComponent;
  let fixture: ComponentFixture<AiAuditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AiAuditComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AiAuditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
