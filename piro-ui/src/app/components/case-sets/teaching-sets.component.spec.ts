import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { CommonModule } from '@angular/common';
import { CaseSetService } from '../../services/case-set.service';
import { LocalStorageService } from '../../services/localStorage.service';
import { ContenttextComponent } from '../common/contenttext/contenttext.component';
import { CatImageUrlPipe } from '../common/contenttext/rtfpipe';
import { TeachingSetsComponent } from './teaching-sets.component';
import { TeachingSetViewComponent } from './teaching-set-view.component';

describe('Teaching set screens', () => {
  let api: jasmine.SpyObj<CaseSetService>;
  beforeEach(async () => {
    api = jasmine.createSpyObj('CaseSetService', ['teachingSets', 'teachingCases']);
    const set = {caseSetId: 7, name: 'GI teaching', creatorName: 'Ada Teacher',
      description: '', specialtyCategory: 'GI', total: 1, createdAt: '', updatedAt: ''};
    api.teachingSets.and.resolveTo({items: [set], total: 1, page: 1, size: 25, categories: ['GI']});
    api.teachingCases.and.resolveTo({set, total: 1, page: 1, size: 1,
      items: [{caseId: 3, ordinal: 1, unavailable: false, summary: {casenumber: 'S26-3', finaltexts: ['Synthetic diagnosis']}}]});
    await TestBed.configureTestingModule({imports: [CommonModule],
      declarations: [TeachingSetsComponent, TeachingSetViewComponent, ContenttextComponent, CatImageUrlPipe], providers: [
      {provide: CaseSetService, useValue: api},
      {provide: LocalStorageService, useValue: {getSearchUrl: () => '', getAdancedFilterData: () => ({})}},
      {provide: ActivatedRoute, useValue: {queryParamMap: of(convertToParamMap({})), paramMap: of(convertToParamMap({id: 7}))}}
    ]}).compileComponents();
  });
  async function render<T>(fixture: ComponentFixture<T>) {
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges(); return fixture.nativeElement as HTMLElement;
  }
  it('labels each public set with its name, creator and specialty', async () => {
    const root = await render(TestBed.createComponent(TeachingSetsComponent));
    const article = root.querySelector('article')!;
    expect(article.textContent).toContain('GI teaching');
    expect(article.textContent).toContain('Ada Teacher'); expect(article.textContent).toContain('GI');
    expect(root.querySelector('#teaching-specialty')).not.toBeNull();
  });
  it('shows a read-only case viewer without owner review, specimen, or sharing controls', async () => {
    const root = await render(TestBed.createComponent(TeachingSetViewComponent));
    expect(root.textContent).toContain('GI teaching'); expect(root.textContent).toContain('Ada Teacher');
    expect(root.textContent).toContain('S26-3'); expect(root.querySelectorAll('input[type=checkbox]').length).toBe(0);
    expect(root.textContent).not.toContain('Reset to unreviewed'); expect(root.textContent).not.toContain('Save sharing settings');
  });
  it('finishes formatting reports without recreating them on every change detection pass', async () => {
    const format = spyOn(CatImageUrlPipe.prototype, 'transform').and.callThrough();
    const fixture = TestBed.createComponent(TeachingSetViewComponent);
    const root = await render(fixture);
    // Bounded passes catch the render loop without hanging the test runner.
    for (let pass = 0; pass < 3; pass++) {
      await fixture.whenStable(); fixture.detectChanges();
    }
    expect(root.querySelector('[role=status]')).toBeNull();
    expect(root.textContent).toContain('Synthetic diagnosis');
    expect(format).toHaveBeenCalledTimes(1);

    const result = await api.teachingCases(7, 1);
    api.teachingCases.and.resolveTo({...result, items: [{caseId: 4, ordinal: 2, unavailable: false,
      summary: {casenumber: 'S26-4', finaltexts: ['Next diagnosis']}}]});
    await fixture.componentInstance.load();
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
    expect(root.textContent).toContain('Next diagnosis');
    expect(root.textContent).not.toContain('Synthetic diagnosis');
    expect(format).toHaveBeenCalledTimes(2);
  });
});
