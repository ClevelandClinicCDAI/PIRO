import { ElementRef } from '@angular/core';
import { TagDisplayDirective } from './tag-display.directive';
import { SearchService } from '../services/search.service';

describe('TagDisplayDirective', () => {
  it('should create an instance', () => {
    const directive = new TagDisplayDirective(
      { nativeElement: {} } as ElementRef,
      {} as SearchService
    );
    expect(directive).toBeTruthy();
  });
});
