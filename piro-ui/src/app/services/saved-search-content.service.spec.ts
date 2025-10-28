import { TestBed } from '@angular/core/testing';

import { SavedSearchContentService } from './saved-search-content.service';

describe('SavedSearchContentService', () => {
  let service: SavedSearchContentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SavedSearchContentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
