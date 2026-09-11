import { ElementRef } from '@angular/core';
import { CommentDisplayDirective } from './comment-display.directive';

describe('CommentDisplayDirective', () => {
  it('should create an instance', () => {
    const directive = new CommentDisplayDirective({
      nativeElement: { children: [{ innerHTML: '' }] }
    } as ElementRef);
    expect(directive).toBeTruthy();
  });
});
