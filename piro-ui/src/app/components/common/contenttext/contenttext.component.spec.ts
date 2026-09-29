import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenttextComponent } from './contenttext.component';
import { CatImageUrlPipe } from './rtfpipe';

describe('ContenttextComponent', () => {
  let component: ContenttextComponent;
  let fixture: ComponentFixture<ContenttextComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ContenttextComponent, CatImageUrlPipe]
    })
      .compileComponents();

    fixture = TestBed.createComponent(ContenttextComponent);
    component = fixture.componentInstance;
    component.inData = { heading: 'Comment', content: [] };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
