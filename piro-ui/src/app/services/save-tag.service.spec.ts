import { TestBed } from '@angular/core/testing';

import { SaveTagService } from './save-tag.service';

describe('SaveTagService', () => {
  let service: SaveTagService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SaveTagService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
