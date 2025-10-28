import { TestBed } from '@angular/core/testing';

import { AivoteService } from './aivote.service';

describe('AivoteService', () => {
  let service: AivoteService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AivoteService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
