import { TestBed } from '@angular/core/testing';

import { CohortService } from './cohort.service';

describe('CohortService', () => {
  let service: CohortService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CohortService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
