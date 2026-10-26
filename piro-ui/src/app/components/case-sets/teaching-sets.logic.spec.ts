import { DefaultIterableDiffer } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CaseSetService, CaseSetSummary, TeachingSetPage, TeachingSetSummary } from '../../services/case-set.service';
import { CaseSetsComponent } from './case-sets.component';
import { TeachingSetsComponent } from './teaching-sets.component';
import { TeachingSetViewComponent } from './teaching-set-view.component';

const teaching: TeachingSetSummary = {caseSetId: 7, name: 'GI teaching', creatorName: 'Ada Teacher',
  description: 'Teaching cases', specialtyCategory: 'GI', total: 2, createdAt: '', updatedAt: ''};
const page = {items: [teaching], total: 1, page: 1, size: 25, categories: ['Derm', 'GI']};

describe('Teaching set browsing logic', () => {
  let api: jasmine.SpyObj<CaseSetService>;
  let router: jasmine.SpyObj<Router>;
  const route = {} as ActivatedRoute;
  beforeEach(() => {
    api = jasmine.createSpyObj('CaseSetService', ['teachingSets', 'teachingCases', 'specialtyCategories', 'share']);
    api.teachingSets.and.resolveTo(page);
    router = jasmine.createSpyObj('Router', ['navigate']); router.navigate.and.resolveTo(true);
  });
  it('loads names, creators and specialties and resets paging when filtering', async () => {
    const component = new TeachingSetsComponent(api, route, router);
    component.specialty = 'GI'; component.page = 3;
    await component.load();
    expect(api.teachingSets).toHaveBeenCalledWith('GI', 3);
    expect(component.items[0].creatorName).toBe('Ada Teacher');
    expect(component.categories).toEqual(['Derm', 'GI']);
    component.specialty = 'Derm'; await component.browse();
    expect(router.navigate).toHaveBeenCalledWith([], {relativeTo: route,
      queryParams: {specialty: 'Derm', page: 1}, queryParamsHandling: 'merge'});
  });
  it('ignores stale catalogue results after a filter change', async () => {
    const component = new TeachingSetsComponent(api, route, router);
    let resolve!: (value: typeof page) => void;
    api.teachingSets.and.returnValue(new Promise(r => resolve = r));
    const old = component.load();
    api.teachingSets.and.resolveTo({...page, items: [], total: 0});
    component.specialty = 'Derm'; await component.load();
    resolve(page); await old;
    expect(component.items).toEqual([]); expect(component.total).toBe(0);
  });
  it('clears stale results on failure instead of presenting them as current public sets', async () => {
    const component = new TeachingSetsComponent(api, route, router);
    await component.load(); api.teachingSets.and.rejectWith({status: 0});
    await component.load();
    expect(component.items).toEqual([]); expect(component.error).toContain('connection');
  });
  it('loads reports without saving owner progress and clears revoked sets', async () => {
    const component = new TeachingSetViewComponent(api, route, router);
    component.id = 7;
    const result: TeachingSetPage = {set: teaching, page: 1, size: 1, total: 2,
      items: [{caseId: 4, ordinal: 1, unavailable: false,
        summary: {finaltexts: ['Synthetic diagnosis'], grosstexts: ['Gross description'], microscopictexts: [' ']}}]};
    api.teachingCases.and.resolveTo(result); await component.load();
    expect(component.reportSections.map(section => section.heading)).toEqual(['Final Diagnosis: ', 'Gross Description: ']);
    await component.go(2);
    expect(router.navigate).toHaveBeenCalledWith([], {relativeTo: route, queryParams: {page: 2}, queryParamsHandling: 'merge'});
    api.teachingCases.and.rejectWith({status: 404, error: {detail: 'Teaching set is no longer public.'}});
    await component.load();
    expect(component.set).toBeNull(); expect(component.member).toBeNull();
    expect(component.error).toContain('no longer public');
  });
  it('keeps report sections stable between screen updates and replaces them for a new case', async () => {
    const component = new TeachingSetViewComponent(api, route, router);
    const result: TeachingSetPage = {set: teaching, page: 1, size: 1, total: 2,
      items: [{caseId: 4, ordinal: 1, unavailable: false,
        summary: {finaltexts: ['Synthetic diagnosis'], grosstexts: ['Gross description']}}]};
    api.teachingCases.and.resolveTo(result); await component.load();
    // NgFor uses this differ: replacing section identities recreates AsyncPipes,
    // whose completed formatting promises trigger another screen update.
    const differ = new DefaultIterableDiffer();
    differ.diff(component.reportSections);
    for (let pass = 0; pass < 3; pass++) {
      expect(differ.diff(component.reportSections)).toBeNull();
    }
    api.teachingCases.and.resolveTo({...result, page: 2, items: [{caseId: 5, ordinal: 2, unavailable: false,
      summary: {microscopictexts: ['Next case report']}}]});
    await component.load();
    expect(component.reportSections).toEqual([{heading: 'Microscopic Description: ', content: ['Next case report']}]);
    expect(differ.diff(component.reportSections)).not.toBeNull();
    expect(differ.diff(component.reportSections)).toBeNull();
    api.teachingCases.and.rejectWith({status: 404}); await component.load();
    expect(component.reportSections).toEqual([]);
  });
  it('requires a category before publishing and updates the owner list on success', async () => {
    const component = new CaseSetsComponent(api, route, router);
    const item = {caseSetId: 7, name: 'GI teaching', isPublic: false, specialtyCategory: null,
      revision: 3, archived: false, captureState: 'READY'} as CaseSetSummary;
    api.specialtyCategories.and.resolveTo(['GI', 'Derm']); component.items = [item];
    await component.startSharing(item); component.isPublic = true;
    await component.saveSharing(); expect(api.share).not.toHaveBeenCalled();
    component.specialtyCategory = 'GI';
    api.share.and.resolveTo({...item, isPublic: true, specialtyCategory: 'GI', revision: 4});
    await component.saveSharing();
    expect(api.share).toHaveBeenCalledWith(item, true, 'GI');
    expect(component.items[0].isPublic).toBeTrue(); expect(component.sharingItem).toBeNull();
    expect(component.notice).toContain('public in Teaching sets');
  });
  it('retains sharing settings on a conflict and allows unpublishing if categories are unavailable', async () => {
    const component = new CaseSetsComponent(api, route, router);
    const item = {caseSetId: 7, name: 'GI teaching', isPublic: true, specialtyCategory: 'GI', revision: 3} as CaseSetSummary;
    api.specialtyCategories.and.rejectWith({status: 503});
    await component.startSharing(item); component.isPublic = false;
    api.share.and.rejectWith({status: 409, error: {detail: 'Reload before saving sharing settings.'}});
    await component.saveSharing();
    expect(api.share).toHaveBeenCalledWith(item, false, 'GI');
    expect(component.sharingItem).toBe(item); expect(component.sharingError).toContain('Reload');
    expect(component.notice).toBe('');
  });
});
