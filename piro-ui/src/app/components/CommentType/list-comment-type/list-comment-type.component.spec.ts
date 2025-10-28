import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListCommentTypeComponent } from './list-comment-type.component';

describe('ListCommentTypeComponent', () => {
  let component: ListCommentTypeComponent;
  let fixture: ComponentFixture<ListCommentTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListCommentTypeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListCommentTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
