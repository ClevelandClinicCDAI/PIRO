import { TestBed } from '@angular/core/testing';

import { RequesthistoryService } from './requesthistory.service';

describe('RequesthistoryService', () => {
  let service: RequesthistoryService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RequesthistoryService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
