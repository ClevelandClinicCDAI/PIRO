import { TestBed } from '@angular/core/testing';

import { SavesearchService } from './savesearch.service';

describe('SavesearchService', () => {
  let service: SavesearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SavesearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
