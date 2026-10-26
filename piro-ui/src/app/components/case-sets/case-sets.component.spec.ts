import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterTestingModule } from '@angular/router/testing';
import { CaseSetsComponent } from './case-sets.component';
import { CaseSetService, CaseSetSummary } from '../../services/case-set.service';

function exampleSet(): CaseSetSummary {
  return {isPublic: false, specialtyCategory: null, caseSetId: 4, name: 'Review set', description: '', sourceType: 'COHORT', sourceId: 1,
    sourceName: 'Cohort', archived: false, revision: 3, createdAt: '2026-10-15T12:00:00Z',
    updatedAt: '2026-10-15T12:00:00Z', captureState: 'READY', captureCursor: '*', captureExpected: 2,
    captureSeen: 2, captureError: '', captureFinishedAt: null, lastCaseId: null, reviewFilter: 'ALL',
    total: 2, unreviewed: 1, included: 1, excluded: 0};
}

describe('CaseSetsComponent', () => {
  let api: jasmine.SpyObj<CaseSetService>;
  let router: jasmine.SpyObj<Router>;
  let component: CaseSetsComponent;
  beforeEach(() => {
    api = jasmine.createSpyObj('CaseSetService', ['list', 'sources', 'create', 'edit', 'delete']);
    api.delete.and.resolveTo();
    router = jasmine.createSpyObj('Router', ['navigate']);
    router.navigate.and.resolveTo(true);
    api.list.and.resolveTo({items: [], total: 0});
    api.sources.and.resolveTo({searches: [{id: 7, name: 'Saved lung search'}], cohorts: []});
    const route = {snapshot: {queryParamMap: convertToParamMap({searchId: 7})}} as ActivatedRoute;
    component = new CaseSetsComponent(api, route, router);
  });

  it('preselects the saved search linked from search results', async () => {
    await component.ngOnInit();
    expect(component.sourceId).toBe(7);
    expect(component.name).toBe('Saved lung search');
    expect(component.items).toEqual([]);
  });

  it('reuses the creation operation after a lost response, but starts a new one for changed input', async () => {
    await component.ngOnInit();
    api.create.and.rejectWith({status: 0});
    await component.create();
    const first = api.create.calls.mostRecent().args[0];
    expect(component.error).toContain('connection');
    await component.create();
    expect(api.create.calls.mostRecent().args[0].operationId).toBe(first.operationId);
    component.name = 'Another set';
    await component.create();
    expect(api.create.calls.mostRecent().args[0].operationId).not.toBe(first.operationId);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('shows the setup error without presenting an empty list as success', async () => {
    api.list.and.rejectWith({status: 503, error: {detail: 'Case sets need a database update.'}});
    await component.load();
    expect(component.error).toContain('database update');
    expect(component.busy).toBeFalse();
  });

  it('requires confirmation naming the set and explaining permanent removal', async () => {
    const item = exampleSet(); component.items = [item];
    const confirm = spyOn(window, 'confirm').and.returnValue(false);
    await component.remove(item);
    expect(confirm.calls.mostRecent().args[0]).toContain('"Review set"');
    expect(confirm.calls.mostRecent().args[0]).toContain('cannot be undone');
    expect(api.delete).not.toHaveBeenCalled(); expect(component.items).toEqual([item]);
  });

  it('deletes an archived set using its revision and moves back from an emptied last page', async () => {
    spyOn(window, 'confirm').and.returnValue(true);
    const item = {...exampleSet(), archived: true};
    component.items = [item]; component.total = 26; component.page = 2; component.archived = true;
    component.editItem = item;
    api.list.and.resolveTo({items: [], total: 25});
    await component.remove(item);
    expect(api.delete).toHaveBeenCalledOnceWith(item);
    expect(api.list).toHaveBeenCalledWith(true, 1);
    expect(component.page).toBe(1); expect(component.editItem).toBeNull();
    expect(component.notice).toContain('removed'); expect(component.busy).toBeFalse();
  });

  it('retains the set and displays a conflict rather than retrying with a newer revision', async () => {
    spyOn(window, 'confirm').and.returnValue(true);
    const item = exampleSet(); component.items = [item]; component.total = 1;
    api.delete.and.rejectWith({status: 409, error: {detail: 'This set changed. Reload before deleting.'}});
    await component.remove(item);
    expect(component.items).toEqual([item]); expect(component.total).toBe(1);
    expect(component.error).toContain('Reload before deleting'); expect(component.notice).toBe('');
    expect(api.list).not.toHaveBeenCalled(); expect(api.delete).toHaveBeenCalledTimes(1);
  });

  it('handles already deleted sets and prevents duplicate in-flight deletion requests', async () => {
    const confirm = spyOn(window, 'confirm').and.returnValue(true);
    const item = exampleSet(); component.items = [item]; component.total = 1;
    let reject!: (error: any) => void;
    api.delete.and.returnValue(new Promise<void>((_, r) => reject = r));
    const removal = component.remove(item);
    await component.remove(item);
    expect(confirm).toHaveBeenCalledTimes(1); expect(api.delete).toHaveBeenCalledTimes(1);
    reject({status: 404}); await removal;
    expect(component.items).toEqual([]); expect(component.error).toBe('');
    expect(component.notice).toContain('removed');
  });
});

describe('Case set Delete button', () => {
  let fixture: ComponentFixture<CaseSetsComponent>;
  let api: jasmine.SpyObj<CaseSetService>;
  beforeEach(async () => {
    api = jasmine.createSpyObj('CaseSetService', ['list', 'sources', 'create', 'edit', 'delete']);
    api.list.and.resolveTo({items: [], total: 0});
    api.sources.and.resolveTo({searches: [], cohorts: []});
    api.delete.and.resolveTo();
    await TestBed.configureTestingModule({
      declarations: [CaseSetsComponent], imports: [FormsModule, CommonModule, RouterTestingModule],
      providers: [{provide: CaseSetService, useValue: api},
        {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: convertToParamMap({})}}}]
    }).compileComponents();
    fixture = TestBed.createComponent(CaseSetsComponent);
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
  });
  for (const archived of [false, true]) {
    it(`renders and confirms deletion for an ${archived ? 'archived' : 'active'} set`, async () => {
      const item = {...exampleSet(), archived};
      fixture.componentInstance.items = [item]; fixture.componentInstance.total = 1;
      fixture.detectChanges();
      const confirm = spyOn(window, 'confirm').and.returnValue(false);
      const button: HTMLButtonElement = fixture.nativeElement.querySelector('button[aria-label="Delete case set Review set"]');
      expect(button.textContent).toBe('Delete');
      button.click(); await fixture.whenStable();
      expect(api.delete).not.toHaveBeenCalled();
      confirm.and.returnValue(true);
      button.click(); await fixture.whenStable(); fixture.detectChanges();
      expect(api.delete).toHaveBeenCalledWith(item);
      expect(fixture.nativeElement.querySelector('article')).toBeNull();
      expect(fixture.nativeElement.querySelector('[role=status]').textContent).toContain('removed');
    });
  }
});
