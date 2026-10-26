import { CommonModule } from '@angular/common';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { CaseSetOperationsComponent } from './case-set-operations.component';
import { CaseSetOperationPreview, CaseSetService, CaseSetSummary } from '../../services/case-set.service';

describe('CaseSetOperationsComponent', () => {
  let fixture: ComponentFixture<CaseSetOperationsComponent>;
  let component: CaseSetOperationsComponent;
  let api: jasmine.SpyObj<CaseSetService>;
  let router: Router;
  const preview: CaseSetOperationPreview = {
    left: {id: 1, name: 'Lung', revision: 3, eligible: 2, total: 3, included: 1, unreviewed: 1, excluded: 1},
    right: {id: 2, name: 'Reviewed', revision: 5, eligible: 4, total: 4, included: 4, unreviewed: 0, excluded: 0},
    total: 5, operation: 'UNION', membership: 'NOT_EXCLUDED'
  };
  beforeEach(async () => {
    api = jasmine.createSpyObj('CaseSetService', ['operationSources', 'previewOperation', 'createOperation']);
    api.operationSources.and.resolveTo([{id: 1, name: 'Lung'}, {id: 2, name: 'Reviewed'}]);
    api.previewOperation.and.resolveTo(preview);
    api.createOperation.and.resolveTo({caseSetId: 12} as CaseSetSummary);
    await TestBed.configureTestingModule({
      declarations: [CaseSetOperationsComponent], imports: [CommonModule, FormsModule, RouterTestingModule],
      providers: [{provide: CaseSetService, useValue: api}]
    }).compileComponents();
    fixture = TestBed.createComponent(CaseSetOperationsComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.resolveTo(true);
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
  });
  async function select(id: string, optionIndex: number) {
    const element: HTMLSelectElement = fixture.nativeElement.querySelector(id);
    element.selectedIndex = optionIndex;
    element.dispatchEvent(new Event('change'));
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
  }
  async function chooseAndPreview() {
    await select('#operation-left', 1);
    await select('#operation-right', 2);
    const form: HTMLFormElement = fixture.nativeElement.querySelector('form');
    form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
  }
  it('selects operands, previews counts and saves a separate set with the preview revisions', async () => {
    expect(fixture.nativeElement.querySelector('h1').textContent).toBe('Case set operations');
    await chooseAndPreview();
    expect(api.previewOperation).toHaveBeenCalledWith({leftSetId: 1, rightSetId: 2, operation: 'UNION', membership: 'NOT_EXCLUDED'});
    expect(fixture.nativeElement.querySelector('#result-heading').textContent).toContain('5 cases');
    const input: HTMLInputElement = fixture.nativeElement.querySelector('#operation-name');
    input.value = 'Combined'; input.dispatchEvent(new Event('input'));
    fixture.detectChanges(); await fixture.whenStable();
    fixture.nativeElement.querySelectorAll('form')[1].dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    await fixture.whenStable();
    expect(api.createOperation.calls.mostRecent().args[0]).toEqual(jasmine.objectContaining({
      name: 'Combined', leftRevision: 3, rightRevision: 5, leftSetId: 1, rightSetId: 2
    }));
    expect(router.navigate).toHaveBeenCalledWith(['/case-sets', 12]);
  });
  it('invalidates preview when changing membership, operation or subtraction direction', async () => {
    await chooseAndPreview();
    await select('#operation-membership', 1);
    expect(component.preview).toBeNull();
    await component.previewOperation();
    expect(api.previewOperation.calls.mostRecent().args[0].membership).toBe('INCLUDED_ONLY');
    await select('#set-operation', 2);
    expect(component.preview).toBeNull();
    expect(fixture.nativeElement.querySelector('#operation-explanation').textContent).toContain('Cases in A');
    await component.previewOperation();
    component.swap(); fixture.detectChanges();
    expect(component.leftSetId).toBe(2); expect(component.rightSetId).toBe(1);
    expect(fixture.nativeElement.querySelector('#result-heading')).toBeNull();
    await component.previewOperation();
    expect(api.previewOperation.calls.mostRecent().args[0]).toEqual({leftSetId: 2, rightSetId: 1, operation: 'DIFFERENCE', membership: 'INCLUDED_ONLY'});
  });
  it('keeps the same creation ID after a lost response and prevents overlapping saves', async () => {
    await chooseAndPreview(); component.name = 'Union';
    api.createOperation.and.rejectWith({status: 0});
    await component.save();
    const first = api.createOperation.calls.mostRecent().args[0];
    await component.save();
    expect(api.createOperation.calls.mostRecent().args[0].operationId).toBe(first.operationId);
    expect(component.error).toContain('connection');
    component.name = 'Other name';
    await component.save();
    expect(api.createOperation.calls.mostRecent().args[0].operationId).not.toBe(first.operationId);
    let resolve!: (value: CaseSetSummary) => void;
    api.createOperation.and.returnValue(new Promise(r => resolve = r));
    const save = component.save();
    await component.save();
    expect(api.createOperation.calls.count()).toBe(4);
    resolve({caseSetId: 12} as CaseSetSummary); await save;
  });
  it('requires a new preview after source changes while retaining the result name', async () => {
    await chooseAndPreview(); component.name = 'Keep this name';
    api.createOperation.and.rejectWith({status: 409, error: {detail: 'A source set changed. Preview again.'}});
    await component.save(); fixture.detectChanges();
    expect(component.preview).toBeNull(); expect(component.name).toBe('Keep this name');
    expect(fixture.nativeElement.querySelector('[role=alert]').textContent).toContain('Preview again');
    await component.save(); expect(api.createOperation.calls.count()).toBe(1);
  });
  it('allows empty results and distinguishes setup errors from an empty source list', async () => {
    api.previewOperation.and.resolveTo({...preview, total: 0});
    await chooseAndPreview();
    expect(fixture.nativeElement.textContent).toContain('You can save an empty set');
    component.name = 'Empty result'; await component.save();
    expect(api.createOperation).toHaveBeenCalled();
    api.operationSources.and.rejectWith({status: 503, error: {detail: 'Case set operations need a database update.'}});
    component.sources = []; await component.loadSources(); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('database update');
    expect(fixture.nativeElement.textContent).not.toContain('No completed sets available');
  });
});
