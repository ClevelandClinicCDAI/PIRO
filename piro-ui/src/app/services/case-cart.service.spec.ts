import { CaseCartService } from './case-cart.service';
import { LocalStorageService } from './localStorage.service';
import { SessionExpiryService } from './session-expiry.service';
import { Router } from '@angular/router';
import { FilterService } from './filter.service';

describe('CaseCartService', () => {
  let cart: CaseCartService;
  beforeEach(() => { localStorage.clear(); cart = new CaseCartService(); });
  afterEach(() => localStorage.clear());

  it('keeps unique selections across navigation and refresh, and removes unchecked cases', () => {
    cart.select(1, 'S26-1', true); cart.select(1, 'S26-1', true); cart.select(2, 'S26-2', true);
    const restored = new CaseCartService();
    expect(restored.items.map(item => item.caseId)).toEqual([1, 2]);
    restored.select(1, 'S26-1', false);
    expect(cart.has(1)).toBeFalse(); expect(cart.count).toBe(1);
  });

  it('clears the live cart when login/logout clears browser storage', () => {
    cart.select(1, 'S26-1', true);
    cart.creation('New set', '', [1]);
    new LocalStorageService().clear();
    expect(cart.items).toEqual([]);
    expect(localStorage.getItem('case-set-cart-create')).toBeNull();
  });

  it('keeps retry identity through reopening or refreshing, and changes it for a different request', () => {
    const first = cart.creation('New set', '', [1]);
    expect(new CaseCartService().creation('New set', '', [1]).operationId).toBe(first.operationId);
    expect(cart.creation('Another set', '', [1]).operationId).not.toBe(first.operationId);
  });

  it('clears selections and pending creation when the current session expires', () => {
    localStorage.setItem('api-token', 'synthetic-token');
    cart.select(1, 'S26-1', true); cart.creation('New set', '', [1]);
    const router = jasmine.createSpyObj<Router>('Router', ['navigate'], {url: '/search'});
    const filter = jasmine.createSpyObj<FilterService>('FilterService', ['setLogin']);
    new SessionExpiryService(router, filter, new LocalStorageService()).expire('synthetic-token');
    expect(cart.count).toBe(0);
    expect(localStorage.getItem('case-set-cart-create')).toBeNull();
  });

  it('caps selections and keeps cases added after a save started', () => {
    for (let id = 1; id <= cart.limit; id++) cart.select(id, `Case ${id}`, true);
    expect(cart.select(String(cart.limit + 1), 'Overflow', true)).toBe('cart-full');
    expect(cart.select('1', 'Case 1', true)).toBe('selected');
    cart.remove([1, 2]);
    expect(cart.count).toBe(cart.limit - 2);
    expect(cart.has(cart.limit)).toBeTrue();
    cart.clear(); expect(cart.count).toBe(0);
  });

  it('accepts numeric string IDs from search and stores integers for case-set requests', () => {
    expect(cart.select('123', 'S26-123', true)).toBe('selected');
    expect(cart.select(123, 'S26-123', true)).toBe('selected');
    expect(cart.has('123')).toBeTrue(); expect(cart.has(123)).toBeTrue();
    expect(cart.items).toEqual([{caseId: 123, label: 'S26-123'}]);
    const restored = new CaseCartService();
    expect(restored.has('123')).toBeTrue();
    expect(restored.creation('Selected cases', '', restored.items.map(item => item.caseId)).caseIds).toEqual([123]);
    expect(restored.select('123', 'S26-123', false)).toBe('selected');
    expect(cart.count).toBe(0);
  });

  it('normalizes previously stored string IDs and deduplicates them with numeric IDs', () => {
    localStorage.setItem('case-set-cart', JSON.stringify([
      {caseId: '123', label: 'S26-123'}, {caseId: 123, label: 'S26-123'}
    ]));
    expect(cart.items).toEqual([{caseId: 123, label: 'S26-123'}]);
    cart.remove(['123']); expect(cart.count).toBe(0);
  });

  it('distinguishes malformed identifiers from a full cart without coercing them to case IDs', () => {
    for (const value of [null, undefined, '', ' ', 'abc', '1.5', '1e3', '0x10', true, [], {}, 0, -1, Infinity, Number.MAX_SAFE_INTEGER + 1]) {
      expect(cart.select(value, 'Invalid', true)).withContext(String(value)).toBe('invalid-case');
      expect(cart.has(value)).toBeFalse();
    }
    expect(cart.count).toBe(0);
  });
});
