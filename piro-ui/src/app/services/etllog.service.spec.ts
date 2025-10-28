import { TestBed } from '@angular/core/testing';

import { EtllogService } from './etllog.service';

describe('ErrorlogService', () => {
  let service: EtllogService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EtllogService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
