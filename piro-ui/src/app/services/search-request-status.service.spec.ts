import { TestBed } from '@angular/core/testing';

import { SearchRequestStatusService } from './search-request-status.service';

describe('SearchRequestStatusService', () => {
  let service: SearchRequestStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SearchRequestStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
