import { TestBed } from '@angular/core/testing';

import { ExtractRequestService } from './extract-request.service';

describe('ExtractRequestService', () => {
  let service: ExtractRequestService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ExtractRequestService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
