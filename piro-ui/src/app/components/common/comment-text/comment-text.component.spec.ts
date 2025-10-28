import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommentTextComponent } from './comment-text.component';

describe('CommentTextComponent', () => {
  let component: CommentTextComponent;
  let fixture: ComponentFixture<CommentTextComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CommentTextComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CommentTextComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
