import { TestBed } from '@angular/core/testing';

import { CommentTypeService } from './comment-type.service';

describe('CommentTypeService', () => {
  let service: CommentTypeService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CommentTypeService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
