import { TestBed } from '@angular/core/testing';

import { SpecimenSourceService } from './specimen-source.service';

describe('SpecimenSourceService', () => {
  let service: SpecimenSourceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SpecimenSourceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
