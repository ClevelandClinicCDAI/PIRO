import { TestBed } from '@angular/core/testing';

import { EthnicityService } from './ethnicity.service';

describe('EthnicityService', () => {
  let service: EthnicityService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EthnicityService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
