import { TestBed } from '@angular/core/testing';

import { SpecimenTypeService } from './specimen-type.service';

describe('SpecimenTypeService', () => {
  let service: SpecimenTypeService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SpecimenTypeService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
