import { Component, Input } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';
import { CaseSetReviewComponent } from './case-set-review.component';
import { CaseSetMember, CaseSetService, CaseSetSummary } from '../../services/case-set.service';

@Component({standalone: false, selector: '[app-contenttext]', template: '{{data.heading}}{{data.content.join(" ")}}'})
class SummaryText {
  @Input('app-contenttext') data: any;
}

function exampleSet(): CaseSetSummary {
  return {isPublic: false, specialtyCategory: null, caseSetId: 4, name: 'Lung review', description: '', sourceType: 'SAVED_SEARCH', sourceId: 7,
    sourceName: 'Lung search', archived: false, revision: 0, createdAt: '2026-10-15T12:00:00Z',
    updatedAt: '2026-10-15T12:00:00Z', captureState: 'READY', captureCursor: 'end', captureExpected: 10,
    captureSeen: 10, captureError: '', captureFinishedAt: '2026-10-15T12:01:00Z', lastCaseId: 11,
    reviewFilter: 'ALL', total: 10, unreviewed: 10, included: 0, excluded: 0};
}
function member(): CaseSetMember {
  return {caseId: 11, ordinal: 6, state: 'UNREVIEWED', reviewedAt: null, revision: 0, unavailable: false,
    summary: {casenumber: 'SYN-11', age: 45, gender: 'F', staffnames: [], interpreters: [], finaltexts: ['Synthetic diagnosis']}};
}

describe('CaseSetReviewComponent', () => {
  let component: CaseSetReviewComponent;
  let fixture: ComponentFixture<CaseSetReviewComponent>;
  let api: jasmine.SpyObj<CaseSetService>;
  let set: CaseSetSummary;
  let row: CaseSetMember;
  beforeEach(async () => {
    set = exampleSet(); row = member();
    api = jasmine.createSpyObj('CaseSetService', ['detail', 'capture', 'members', 'decide', 'position', 'specimens', 'selectSpecimens']);
    api.detail.and.resolveTo(set);
    api.members.and.resolveTo({set, items: [row], total: 10, page: 6, size: 1, filter: 'ALL'});
    api.position.and.resolveTo({});
    api.specimens.and.callFake(async () => ({specimens: [], member: {}, set: component.set ?? set}));
    await TestBed.configureTestingModule({
      declarations: [CaseSetReviewComponent, SummaryText], imports: [FormsModule, CommonModule, RouterTestingModule],
      providers: [{provide: CaseSetService, useValue: api},
        {provide: ActivatedRoute, useValue: {snapshot: {paramMap: convertToParamMap({id: 4})}}}],
    }).compileComponents();
    fixture = TestBed.createComponent(CaseSetReviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
  });

  it('resumes at the exact saved case and renders one diagnosis and case detail link', () => {
    expect(api.members).toHaveBeenCalledWith(4, 'ALL', 1, 1, true);
    expect(component.page).toBe(6);
    expect(fixture.nativeElement.querySelectorAll('.case-review-card').length).toBe(1);
    expect(fixture.nativeElement.textContent).toContain('Synthetic diagnosis');
    const link = fixture.nativeElement.querySelector('a[href="/search-detail/11"]');
    expect(link.textContent).toContain('SYN-11');
  });

  it('keeps the decision and progress unchanged when saving fails', async () => {
    api.decide.and.rejectWith({status: 0});
    await component.decide(row, 'EXCLUDED');
    expect(row.state).toBe('UNREVIEWED');
    expect(component.reviewed).toBe(0);
    expect(component.error).toContain('connection');
    expect(component.pendingCaseId).toBeNull();
    expect(component.saved).toBe('');
  });

  it('updates status and progress only after the decision is acknowledged', async () => {
    const updated = {...set, excluded: 1, unreviewed: 9};
    const next = {...member(), caseId: 12, ordinal: 7};
    api.members.and.resolveTo({set: updated, items: [next], total: 10, page: 7, size: 1, filter: 'ALL'});
    let resolve!: (value: any) => void;
    api.decide.and.returnValue(new Promise(r => resolve = r));
    const work = component.decide(row, 'EXCLUDED');
    await component.decide(row, 'INCLUDED');
    await component.go(8);
    expect(component.page).toBe(6);
    expect(api.decide).toHaveBeenCalledTimes(1);
    expect(row.state).toBe('UNREVIEWED');
    expect(component.currentMember).toBe(row);
    resolve({set: updated, member: {state: 'EXCLUDED', revision: 1}});
    await work;
    expect(row.state).toBe('EXCLUDED');
    expect(component.reviewed).toBe(1);
    expect(api.members).toHaveBeenCalledWith(4, 'ALL', 7, 1, false);
    expect(component.currentMember).toBe(next);
    expect(api.position).toHaveBeenCalledWith(4, 12, 'ALL');
    expect(component.saved).toContain('saved');
  });

  it('saves browsing position without marking cases reviewed', async () => {
    await component.go(2);
    expect(api.position).toHaveBeenCalledWith(4, 11, 'ALL');
    expect(api.decide).not.toHaveBeenCalled();
    expect(component.reviewed).toBe(0);
  });

  it('stops capture after the in-flight batch when the page is left', async () => {
    component.set = {...set, captureState: 'CAPTURING', captureCursor: '*'};
    let resolve!: (value: CaseSetSummary) => void;
    api.capture.and.returnValue(new Promise(r => resolve = r));
    const work = component.capture();
    component.ngOnDestroy();
    resolve({...set, captureState: 'CAPTURING', captureCursor: 'next'});
    await work;
    expect(api.capture).toHaveBeenCalledTimes(1);
    expect(component.capturing).toBeFalse();
  });

  it('retains unavailable members in the review view', () => {
    row.summary = null; row.unavailable = true;
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('saved membership and review decision have been retained');
    expect(component.set?.total).toBe(10);
  });

  it('renders all six report sections in the requested order', () => {
    Object.assign(row.summary, {finaltexts: ['Final text'], commenttexts: ['Diagnostic comment text'],
      grosstexts: ['Gross text'], synoptictexts: ['Synoptic text'], intraoptexts: ['Intraoperative text'],
      microscopictexts: ['Microscopic text']});
    fixture.detectChanges();
    const sections = fixture.debugElement.queryAll(By.directive(SummaryText));
    expect(sections.map(section => section.componentInstance.data.heading.trim())).toEqual([
      'Final Diagnosis:', 'Diagnostic Comment:', 'Gross Description:', 'Synoptic:',
      'Intraoperative Diagnosis:', 'Microscopic Description:'
    ]);
    expect(sections.map(section => section.nativeElement.textContent)).toEqual([
      'Final Diagnosis: Final text', 'Diagnostic Comment: Diagnostic comment text',
      'Gross Description: Gross text', 'Synoptic: Synoptic text',
      'Intraoperative Diagnosis: Intraoperative text', 'Microscopic Description: Microscopic text'
    ]);
  });

  it('omits missing and blank sections and clears previous reports when moving to another case', async () => {
    row.summary.grosstexts = ['Gross report for first case'];
    fixture.detectChanges();
    const next = {...member(), caseId: 12, ordinal: 7, summary: {finaltexts: null, commenttexts: [' ', null],
      grosstexts: [], intraoptexts: undefined, microscopictexts: ['Only microscopic text']}};
    api.members.and.resolveTo({set, items: [next], total: 10, page: 7, size: 1, filter: 'ALL'});
    await component.go(7); fixture.detectChanges();
    const sections = fixture.debugElement.queryAll(By.directive(SummaryText));
    expect(sections.length).toBe(1);
    expect(sections[0].nativeElement.textContent).toBe('Microscopic Description: Only microscopic text');
    expect(fixture.nativeElement.textContent).not.toContain('Gross report for first case');
    next.summary.microscopictexts = [];
    fixture.detectChanges();
    expect(fixture.debugElement.queryAll(By.directive(SummaryText)).length).toBe(0);
    expect(fixture.nativeElement.textContent).toContain('No report text is available for this case.');
  });

  it('keeps the controls above one case in the same position for long and short summaries', async () => {
    row.summary.finaltexts = ['Long diagnosis '.repeat(2000)];
    fixture.detectChanges();
    const include: HTMLButtonElement = fixture.nativeElement.querySelector('.review-decision');
    const before = include.getBoundingClientRect();
    const content: HTMLElement = fixture.nativeElement.querySelector('.case-review-content');
    expect(content.scrollHeight).toBeGreaterThan(content.clientHeight);
    content.scrollTop = 200;
    const next = {...member(), caseId: 12, ordinal: 7, summary: {...member().summary, casenumber: 'SYN-12'}};
    api.members.and.resolveTo({set, items: [next], total: 10, page: 7, size: 1, filter: 'ALL'});
    const nextButton: HTMLButtonElement = fixture.nativeElement.querySelector('.review-navigation button:last-child');
    nextButton.click();
    await fixture.whenStable(); fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('.case-review-card').length).toBe(1);
    expect(fixture.nativeElement.querySelector('a[href="/search-detail/11"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('a[href="/search-detail/12"]')).not.toBeNull();
    const after = include.getBoundingClientRect();
    expect(after.top).toBe(before.top); expect(after.left).toBe(before.left);
    expect(after.bottom).toBeLessThan(fixture.nativeElement.querySelector('.case-review-card').getBoundingClientRect().top);
    expect(content.scrollTop).toBe(0);
    expect(api.decide).not.toHaveBeenCalled();
  });

  it('does not skip the next unreviewed case when a decision removes the current case from the filter', async () => {
    component.filter = 'UNREVIEWED'; component.page = 2; component.total = 3;
    const next = {...member(), caseId: 12, ordinal: 7};
    const updated = {...set, included: 1, unreviewed: 2};
    api.decide.and.resolveTo({set: updated, member: {state: 'INCLUDED', revision: 1}});
    api.members.and.resolveTo({set: updated, items: [next], total: 2, page: 2, size: 1, filter: 'UNREVIEWED'});
    await component.decide(row, 'INCLUDED');
    expect(api.members.calls.mostRecent().args).toEqual([4, 'UNREVIEWED', 2, 1, false]);
    expect(component.currentMember).toBe(next);
    expect(api.position).toHaveBeenCalledWith(4, 12, 'UNREVIEWED');
  });

  it('stays on the last case after a decision, and reset does not advance', async () => {
    component.page = 10;
    api.members.calls.reset();
    api.decide.and.resolveTo({set: {...set, included: 1, unreviewed: 9}, member: {state: 'INCLUDED', revision: 1}});
    await component.decide(row, 'INCLUDED'); fixture.detectChanges();
    expect(component.currentMember).toBe(row);
    expect(component.saved).toContain('Last case');
    expect(fixture.nativeElement.querySelector('.review-navigation button:last-child').disabled).toBeTrue();
    component.page = 6;
    api.decide.and.resolveTo({set, member: {state: 'UNREVIEWED', revision: 2}});
    await component.decide(row, 'UNREVIEWED');
    expect(api.members).not.toHaveBeenCalled();
    expect(component.currentMember).toBe(row);
  });

  it('keeps the current case and position after failed navigation or filter changes', async () => {
    api.members.and.rejectWith({status: 0});
    api.position.calls.reset();
    await component.go(7);
    expect(component.page).toBe(6); expect(component.currentMember).toBe(row);
    const select: HTMLSelectElement = fixture.nativeElement.querySelector('#review-filter');
    select.value = 'INCLUDED'; select.dispatchEvent(new Event('change'));
    await fixture.whenStable(); fixture.detectChanges(); await fixture.whenStable();
    expect(component.filter).toBe('ALL'); expect(select.value).toBe('ALL');
    expect(api.position).not.toHaveBeenCalled();
    expect(component.error).toContain('connection');
  });

  it('retains the saved decision on the current case if loading the next case fails', async () => {
    api.decide.and.resolveTo({set: {...set, excluded: 1, unreviewed: 9}, member: {state: 'EXCLUDED', revision: 1}});
    api.members.and.rejectWith({status: 0});
    await component.decide(row, 'EXCLUDED');
    expect(component.page).toBe(6); expect(component.currentMember).toBe(row);
    expect(row.state).toBe('EXCLUDED'); expect(component.reviewed).toBe(1);
    expect(component.saved).toContain('Decision saved');
    expect(component.error).toContain('connection');
  });

  it('disables review and navigation when the final unreviewed case leaves the view', async () => {
    component.filter = 'UNREVIEWED'; component.page = 1; component.total = 1;
    const updated = {...set, unreviewed: 0, included: 10};
    api.decide.and.resolveTo({set: updated, member: {state: 'INCLUDED', revision: 1}});
    api.members.and.resolveTo({set: updated, items: [], total: 0, page: 1, size: 1, filter: 'UNREVIEWED'});
    await component.decide(row, 'INCLUDED'); fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('.case-review-card').length).toBe(0);
    expect(fixture.nativeElement.textContent).toContain('No cases match this review filter');
    const buttons: HTMLButtonElement[] = Array.from(fixture.nativeElement.querySelectorAll('.review-controls-row button'));
    expect(buttons.every(button => button.disabled)).toBeTrue();
    expect(api.position).toHaveBeenCalledWith(4, null, 'UNREVIEWED');
  });

  async function showSpecimens() {
    api.specimens.and.resolveTo({set, member: {}, specimens: [
      {specimenId: 101, part: 'A', selected: true, available: true},
      {specimenId: 102, part: 'B', selected: false, available: true}
    ]});
    await component.loadSpecimens(); fixture.detectChanges();
  }

  it('shows saved specimen parts on the right with a partially checked select all', async () => {
    await showSpecimens();
    const panel: HTMLElement = fixture.nativeElement.querySelector('.specimen-panel');
    const content: HTMLElement = fixture.nativeElement.querySelector('.case-review-content');
    if (window.matchMedia('(max-width: 760px)').matches) {
      expect(panel.getBoundingClientRect().top).toBeGreaterThanOrEqual(content.getBoundingClientRect().bottom);
    } else {
      expect(panel.getBoundingClientRect().left).toBeGreaterThanOrEqual(content.getBoundingClientRect().right);
    }
    const inputs = panel.querySelectorAll('input');
    expect(inputs.length).toBe(3);
    expect(inputs[0].indeterminate).toBeTrue();
    expect(inputs[1].checked).toBeTrue(); expect(inputs[2].checked).toBeFalse();
    expect(panel.textContent).toContain('1 selected');
  });

  it('saves a checkbox before enabling navigation or Include, without advancing the case', async () => {
    await showSpecimens();
    let resolve!: (value: any) => void;
    api.selectSpecimens.and.returnValue(new Promise(r => resolve = r));
    const checkbox: HTMLInputElement = fixture.nativeElement.querySelectorAll('.specimen-choice input')[2];
    checkbox.click(); fixture.detectChanges();
    expect(api.selectSpecimens).toHaveBeenCalledWith(4, row, [101, 102]);
    expect(component.controlsDisabled).toBeTrue();
    expect(fixture.nativeElement.querySelector('.review-decision').disabled).toBeTrue();
    await component.go(7); await component.decide(row, 'INCLUDED');
    expect(api.decide).not.toHaveBeenCalled();
    expect(component.page).toBe(6); expect(checkbox.checked).toBeFalse();
    resolve({set: {...set, revision: 1}, member: {revision: 1},
      specimens: component.specimens.map(s => ({...s, selected: true}))});
    await fixture.whenStable(); fixture.detectChanges();
    expect(checkbox.checked).toBeTrue(); expect(row.revision).toBe(1);
    expect(component.page).toBe(6); expect(row.state).toBe('UNREVIEWED');
    expect(component.specimenSaved).toContain('saved');
  });

  it('selects all specimens and clears all with one saved update each', async () => {
    await showSpecimens();
    api.selectSpecimens.and.callFake(async (_, member, ids) => ({set, member: {revision: member.revision + 1},
      specimens: component.specimens.map(s => ({...s, selected: ids.includes(s.specimenId)}))}));
    const selectAll: HTMLInputElement = fixture.nativeElement.querySelector('.specimen-select-all input');
    selectAll.click(); await fixture.whenStable(); fixture.detectChanges();
    expect(component.selectedSpecimenCount).toBe(2); expect(selectAll.checked).toBeTrue();
    expect(selectAll.indeterminate).toBeFalse();
    selectAll.click(); await fixture.whenStable(); fixture.detectChanges();
    expect(component.selectedSpecimenCount).toBe(0); expect(selectAll.checked).toBeFalse();
    expect(api.selectSpecimens.calls.mostRecent().args[2]).toEqual([]);
  });

  it('restores the checkbox and shows an error if the save fails', async () => {
    await showSpecimens();
    api.selectSpecimens.and.rejectWith({status: 0});
    const checkbox: HTMLInputElement = fixture.nativeElement.querySelectorAll('.specimen-choice input')[2];
    checkbox.click(); await fixture.whenStable(); fixture.detectChanges();
    expect(checkbox.checked).toBeFalse(); expect(component.selectedSpecimenCount).toBe(1);
    expect(component.specimenError).toContain('could not be saved');
    expect(component.specimenSaved).toBe(''); expect(row.revision).toBe(0);
    expect(component.currentMember).toBe(row);
  });

  it('loads the next case selections without carrying the previous case checkboxes', async () => {
    await showSpecimens();
    const next = {...member(), caseId: 12, ordinal: 7};
    api.members.and.resolveTo({set, items: [next], total: 10, page: 7, size: 1, filter: 'ALL'});
    api.specimens.and.resolveTo({set, member: {}, specimens: [{specimenId: 201, part: 'C', selected: false, available: true}]});
    await component.go(7); fixture.detectChanges();
    expect(api.specimens.calls.mostRecent().args).toEqual([4, 12]);
    expect(component.specimens.map(s => s.specimenId)).toEqual([201]);
    expect(component.selectedSpecimenCount).toBe(0);
    expect(fixture.nativeElement.querySelectorAll('.specimen-choice input').length).toBe(2);
  });

  it('shows specimen setup errors while keeping ordinary review available', async () => {
    api.specimens.and.rejectWith({status: 503, error: {detail: 'Run 20261015_AddCaseSetSpecimens.sql.'}});
    await component.loadSpecimens(); fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.specimen-panel').textContent).toContain('20261015_AddCaseSetSpecimens.sql');
    expect(component.specimensLoaded).toBeFalse();
    expect(fixture.nativeElement.querySelector('.review-decision').disabled).toBeFalse();
    expect(component.currentMember).toBe(row);
  });
});
