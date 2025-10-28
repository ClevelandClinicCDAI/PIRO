import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenttextComponent } from './contenttext.component';

describe('ContenttextComponent', () => {
  let component: ContenttextComponent;
  let fixture: ComponentFixture<ContenttextComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContenttextComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContenttextComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
