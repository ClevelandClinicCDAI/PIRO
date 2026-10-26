import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { CaseCartComponent } from './case-cart.component';
import { CaseCartService } from '../../services/case-cart.service';
import { CaseSetService, CaseSetSummary } from '../../services/case-set.service';

describe('CaseCartComponent', () => {
  let fixture: ComponentFixture<CaseCartComponent>;
  let component: CaseCartComponent;
  let api: jasmine.SpyObj<CaseSetService>;
  let modal: jasmine.SpyObj<NgbActiveModal>;
  let cart: CaseCartService;
  const saved = {caseSetId: 7, name: 'Selected cases'} as CaseSetSummary;
  beforeEach(async () => {
    localStorage.clear(); cart = new CaseCartService();
    cart.select(1, 'S26-1', true); cart.select(2, 'S26-2', true);
    api = jasmine.createSpyObj('CaseSetService', ['cartTargets', 'createFromCart', 'addCases']);
    api.cartTargets.and.resolveTo([{id: 7, name: 'Selected cases'}]);
    api.createFromCart.and.resolveTo(saved);
    api.addCases.and.resolveTo({set: saved, added: 1, alreadyPresent: 1});
    modal = jasmine.createSpyObj('NgbActiveModal', ['close', 'dismiss']);
    await TestBed.configureTestingModule({imports: [CaseCartComponent], providers: [
      {provide: CaseSetService, useValue: api}, {provide: NgbActiveModal, useValue: modal},
      {provide: CaseCartService, useValue: cart}
    ]}).compileComponents();
    fixture = TestBed.createComponent(CaseCartComponent); component = fixture.componentInstance;
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
  });
  afterEach(() => localStorage.clear());

  it('renders cart cases, removes a case, and creates a named set with only the remaining selection', async () => {
    const root: HTMLElement = fixture.nativeElement;
    expect(root.querySelectorAll('.cart-cases li').length).toBe(2);
    (root.querySelector('[aria-label="Remove S26-1 from cart"]') as HTMLButtonElement).click();
    const name = root.querySelector('#cart-set-name') as HTMLInputElement;
    name.value = 'Selected cases'; name.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    (root.querySelector('button[type=submit]') as HTMLButtonElement).click();
    await fixture.whenStable(); fixture.detectChanges();
    expect(api.createFromCart.calls.mostRecent().args[0].caseIds).toEqual([2]);
    expect(api.createFromCart.calls.mostRecent().args[0].name).toBe('Selected cases');
    expect(cart.count).toBe(0); expect(modal.close).toHaveBeenCalled();
  });

  it('adds to an existing set and reports skipped duplicates', async () => {
    const root: HTMLElement = fixture.nativeElement;
    (root.querySelector('input[value=EXISTING]') as HTMLInputElement).click();
    fixture.detectChanges(); await fixture.whenStable(); fixture.detectChanges();
    expect(root.querySelector('#cart-target')?.textContent).toContain('Selected cases');
    component.targetId = 7; await component.save();
    expect(api.addCases).toHaveBeenCalledOnceWith(7, [1, 2]);
    expect(modal.close).toHaveBeenCalledWith({set: saved, added: 1, alreadyPresent: 1});
    expect(cart.count).toBe(0);
  });

  it('retains cases and retry identity after a failed save', async () => {
    component.name = 'Selected cases'; api.createFromCart.and.rejectWith({status: 0});
    await component.save(); const first = api.createFromCart.calls.mostRecent().args[0];
    expect(cart.count).toBe(2); expect(modal.close).not.toHaveBeenCalled();
    expect(component.error).toContain('connection');
    await component.save();
    expect(api.createFromCart.calls.mostRecent().args[0].operationId).toBe(first.operationId);
  });

  it('prevents duplicate submissions and keeps selections added while saving', async () => {
    component.name = 'Selected cases';
    let resolve!: (set: CaseSetSummary) => void;
    api.createFromCart.and.returnValue(new Promise(r => resolve = r));
    const request = component.save(); await component.save();
    fixture.detectChanges();
    expect((fixture.nativeElement.querySelector('button[type=submit]') as HTMLButtonElement).disabled).toBeTrue();
    expect(api.createFromCart).toHaveBeenCalledTimes(1);
    cart.select(3, 'S26-3', true); resolve(saved); await request;
    expect(cart.items.map(item => item.caseId)).toEqual([3]);
  });

  it('shows target load errors and allows retry without losing the cart', async () => {
    api.cartTargets.and.rejectWith({status: 503, error: {detail: 'Case sets need setup.'}});
    await component.loadTargets(); component.mode = 'EXISTING'; component.targetId = 7;
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Case sets need setup.');
    await component.save(); expect(api.addCases).not.toHaveBeenCalled(); expect(cart.count).toBe(2);
    api.cartTargets.and.resolveTo([{id: 7, name: 'Selected cases'}]);
    await component.loadTargets(); expect(component.targetsError).toBe('');
  });
});
