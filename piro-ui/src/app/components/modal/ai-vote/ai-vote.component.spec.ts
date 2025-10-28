import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AiVoteComponent } from './ai-vote.component';

describe('AiVoteComponent', () => {
  let component: AiVoteComponent;
  let fixture: ComponentFixture<AiVoteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AiVoteComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AiVoteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
