import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateCommentTypeComponent } from './create-comment-type.component';

describe('CreateCommentTypeComponent', () => {
  let component: CreateCommentTypeComponent;
  let fixture: ComponentFixture<CreateCommentTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateCommentTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateCommentTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
