import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateCommentTypeComponent } from './update-comment-type.component';

describe('UpdateCommentTypeComponent', () => {
  let component: UpdateCommentTypeComponent;
  let fixture: ComponentFixture<UpdateCommentTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UpdateCommentTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateCommentTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
