import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CaseSetCreate, CaseSetService, CaseSetSources, CaseSetSummary, caseSetError } from '../../services/case-set.service';

@Component({standalone: false, selector: 'app-case-sets',
  templateUrl: './case-sets.component.html', styleUrls: ['./case-sets.css']})
export class CaseSetsComponent implements OnInit {
  sources: CaseSetSources = {searches: [], cohorts: []};
  items: CaseSetSummary[] = [];
  name = ''; description = ''; sourceType: 'SAVED_SEARCH' | 'COHORT' = 'SAVED_SEARCH';
  sourceId: number | null = null;
  archived = false; page = 1; total = 0; busy = false; creating = false; error = '';
  notice = '';
  editItem: CaseSetSummary | null = null; editName = ''; editDescription = '';
  private pendingCreate: CaseSetCreate | null = null;
  sharingItem: CaseSetSummary | null = null;
  isPublic = false; specialtyCategory = ''; specialties: string[] = [];
  sharingBusy = false; sharingError = ''; categoriesError = '';
  constructor(private api: CaseSetService, private route: ActivatedRoute, private router: Router) {}

  async ngOnInit() {
    await this.load();
    try {
      this.sources = await this.api.sources();
      const searchId = Number(this.route.snapshot.queryParamMap.get('searchId'));
      if (this.sources.searches.some(s => s.id === searchId)) {
        this.sourceId = searchId;
        this.chooseSource();
      }
    } catch (error) { this.error = caseSetError(error); }
  }

  get availableSources() { return this.sourceType === 'SAVED_SEARCH' ? this.sources.searches : this.sources.cohorts; }
  changeType() { this.sourceId = null; this.name = ''; }
  chooseSource() {
    const source = this.availableSources.find(s => s.id === Number(this.sourceId));
    if (source) this.name = source.name;
  }
  async load() {
    this.busy = true; this.error = '';
    try {
      const result = await this.api.list(this.archived, this.page);
      this.items = result.items; this.total = result.total;
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
  async create() {
    if (this.creating || !this.sourceId || !this.name.trim()) return;
    this.creating = true; this.error = '';
    const draft = {name: this.name.trim(), description: this.description, sourceType: this.sourceType, sourceId: Number(this.sourceId)};
    if (!this.pendingCreate || JSON.stringify({...this.pendingCreate, operationId: undefined}) !== JSON.stringify(draft)) {
      this.pendingCreate = {...draft, operationId: crypto.randomUUID()};
    }
    try {
      const set = await this.api.create(this.pendingCreate);
      await this.router.navigate(['/case-sets', set.caseSetId]);
      this.pendingCreate = null;
    } catch (error) { this.error = caseSetError(error); }
    finally { this.creating = false; }
  }
  startEdit(item: CaseSetSummary) { this.editItem = item; this.editName = item.name; this.editDescription = item.description; }
  async startSharing(item: CaseSetSummary) {
    if (this.sharingBusy) return;
    this.sharingItem = item; this.isPublic = item.isPublic;
    this.specialtyCategory = item.specialtyCategory || '';
    this.sharingError = ''; this.categoriesError = ''; this.sharingBusy = true;
    try { this.specialties = await this.api.specialtyCategories(); }
    catch (error) { this.categoriesError = caseSetError(error); }
    finally { this.sharingBusy = false; }
  }
  async saveSharing() {
    if (!this.sharingItem || this.sharingBusy || (this.isPublic && (!this.specialtyCategory || !!this.categoriesError))) return;
    this.sharingBusy = true; this.sharingError = ''; this.notice = '';
    try {
      const set = await this.api.share(this.sharingItem, this.isPublic, this.specialtyCategory || null);
      this.items = this.items.map(item => item.caseSetId === set.caseSetId ? set : item);
      this.sharingItem = null;
      this.notice = set.isPublic ? `"${set.name}" is public in Teaching sets.` : `"${set.name}" is private.`;
    } catch (error) { this.sharingError = caseSetError(error); }
    finally { this.sharingBusy = false; }
  }
  async saveEdit() {
    if (!this.editItem || !this.editName.trim() || this.busy) return;
    this.busy = true; this.error = '';
    try {
      await this.api.edit(this.editItem, this.editName.trim(), this.editDescription, this.editItem.archived);
      this.editItem = null;
      await this.load();
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
  async archive(item: CaseSetSummary) {
    if (this.busy) return;
    this.busy = true; this.error = '';
    try {
      await this.api.edit(item, item.name, item.description, !item.archived);
      this.page = 1;
      await this.load();
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
  async remove(item: CaseSetSummary) {
    if (this.busy || this.creating) return;
    if (!window.confirm(`Permanently delete case set "${item.name}"?\n\nThis removes its saved case memberships and review history. The underlying cases, saved searches, cohorts, and other case sets are kept.\n\nThis cannot be undone.`)) return;
    this.busy = true; this.error = ''; this.notice = '';
    try {
      try { await this.api.delete(item); }
      catch (error: any) {
        // A retry after a lost response can find the set already deleted.
        if (error?.status !== 404) throw error;
      }
      this.items = this.items.filter(set => set.caseSetId !== item.caseSetId);
      this.total = Math.max(0, this.total - 1);
      this.page = Math.min(this.page, Math.max(1, Math.ceil(this.total / 25)));
      if (this.editItem?.caseSetId === item.caseSetId) this.editItem = null;
      this.notice = `Case set "${item.name}" removed.`;
      await this.load();
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
}
