import { Injectable } from '@angular/core';
import { CaseSetCartCreate } from './case-set.service';

export interface CartCase { caseId: number; label: string; }
export type CartSelectionResult = 'selected' | 'invalid-case' | 'cart-full';

@Injectable({providedIn: 'root'})
export class CaseCartService {
  readonly limit = 1000;
  private readonly key = 'case-set-cart';
  private readonly pendingKey = 'case-set-cart-create';
  private cachedRaw = '';
  private cachedItems: CartCase[] = [];

  private caseId(value: unknown): number | null {
    // Search/Solr IDs can be numeric strings; memberships use integer IDs.
    if (typeof value === 'string' && /^\d+$/.test(value.trim())) value = Number(value.trim());
    return typeof value === 'number' && Number.isSafeInteger(value) && value > 0 ? value : null;
  }

  // Login, logout and expiry already clear localStorage. Read through it so
  // navigating, refreshing and other tabs see the current login's selection.
  get items(): readonly CartCase[] {
    try {
      const raw = localStorage.getItem(this.key) || '[]';
      if (raw === this.cachedRaw) return this.cachedItems;
      this.cachedRaw = raw;
      this.cachedItems = [];
      const saved = JSON.parse(raw);
      if (!Array.isArray(saved)) return this.cachedItems;
      const unique = new Map<number, CartCase>();
      for (const item of saved) {
        const caseId = this.caseId(item?.caseId);
        if (caseId !== null && typeof item.label === 'string') {
          unique.set(caseId, {caseId, label: item.label});
        }
      }
      this.cachedItems = Array.from(unique.values()).slice(0, this.limit);
      return this.cachedItems;
    } catch { return []; }
  }
  get count() { return this.items.length; }
  has(value: unknown) {
    const caseId = this.caseId(value);
    return caseId !== null && this.items.some(item => item.caseId === caseId);
  }
  select(value: unknown, label: string, selected: boolean): CartSelectionResult {
    const caseId = this.caseId(value);
    if (caseId === null) return 'invalid-case';
    const items = this.items;
    if (!selected) { this.remove([caseId]); return 'selected'; }
    if (items.some(item => item.caseId === caseId)) return 'selected';
    if (items.length >= this.limit) return 'cart-full';
    // Only the already displayed accession is kept, never patient/report text.
    localStorage.setItem(this.key, JSON.stringify([...items, {caseId, label}]));
    return 'selected';
  }
  remove(caseIds: readonly unknown[]) {
    const removed = new Set(caseIds.map(value => this.caseId(value)));
    localStorage.setItem(this.key, JSON.stringify(this.items.filter(item => !removed.has(item.caseId))));
  }
  clear() { localStorage.removeItem(this.key); }
  creation(name: string, description: string, caseIds: number[]): CaseSetCartCreate {
    const draft = {name, description, caseIds};
    let pending: CaseSetCartCreate | null = null;
    try { pending = JSON.parse(localStorage.getItem(this.pendingKey) || 'null'); } catch {}
    if (pending && JSON.stringify({name: pending.name, description: pending.description, caseIds: pending.caseIds}) === JSON.stringify(draft)) {
      return pending;
    }
    const payload = {...draft, operationId: crypto.randomUUID()};
    localStorage.setItem(this.pendingKey, JSON.stringify(payload));
    return payload;
  }
  completeCreation() { localStorage.removeItem(this.pendingKey); }
}
