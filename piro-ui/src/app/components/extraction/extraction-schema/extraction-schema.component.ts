import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, switchMap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { ExtractionService } from '../../../services/extraction.service';
import { SavedSearchContentService } from '../../../services/saved-search-content.service';

export interface FieldDefinition {
  name: string;
  type: 'text' | 'categorical' | 'boolean' | 'number' | 'date';
  hint: string;
  enumValues: string[];
  minimum: number | null;
  maximum: number | null;
  _enumInput?: string;  // temporary binding for adding enum values
}

@Component({
  selector: 'app-extraction-schema',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './extraction-schema.component.html',
  styleUrls: ['./extraction-schema.component.css']
})
export class ExtractionSchemaComponent implements OnInit, OnDestroy {
  sessionId!: number;
  session: any = null;
  queuedCases: any[] = [];
  fields: FieldDefinition[] = [];

  // Preview panel state
  selectedCaseId: number | null = null;
  previewResult: any = null;
  previewLoading = false;
  previewError: string | null = null;
  reportText = '';
  highlightedReportHtml = '';

  saving = false;
  suggesting = false;
  loadingSession = true;

  // Saved search loader
  savedSearches: any[] = [];
  selectedSearchId: number | null = null;
  showSearchPicker = false;
  loadingFromSearch = false;

  private schemaChange$ = new Subject<void>();
  private previewSub?: Subscription;
  private subs: Subscription[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private extractionService: ExtractionService,
    private savedSearchContentService: SavedSearchContentService,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.sessionId = parseInt(this.route.snapshot.paramMap.get('id') || '0', 10);
    this.loadSession();
    this.setupPreviewDebounce();
  }

  ngOnDestroy(): void {
    this.subs.forEach(s => s.unsubscribe());
    if (this.previewSub) this.previewSub.unsubscribe();
  }

  async loadSession() {
    this.loadingSession = true;
    try {
      this.session = await this.extractionService.getSession(this.sessionId);
      if (this.session?.SchemaJson) {
        this.fields = this.schemaJsonToFields(JSON.parse(this.session.SchemaJson));
      }
      this.queuedCases = await this.extractionService.getQueue(this.sessionId) ?? [];
      if (this.queuedCases.length > 0) {
        this.selectedCaseId = this.queuedCases[0].CaseId;
        this.loadCaseText();
      }
    } catch (e) {
      this.toastr.error('Failed to load session.');
    } finally {
      this.loadingSession = false;
    }
  }

  // ── Field management ─────────────────────────────────────────────────────

  addField() {
    this.fields.push({
      name: '',
      type: 'text',
      hint: '',
      enumValues: [],
      minimum: null,
      maximum: null,
      _enumInput: ''
    });
    this.onSchemaChanged();
  }

  removeField(index: number) {
    this.fields.splice(index, 1);
    this.onSchemaChanged();
  }

  moveField(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= this.fields.length) return;
    [this.fields[index], this.fields[target]] = [this.fields[target], this.fields[index]];
    this.onSchemaChanged();
  }

  addEnumValue(field: FieldDefinition) {
    const val = (field._enumInput || '').trim();
    if (val && !field.enumValues.includes(val)) {
      field.enumValues.push(val);
      field._enumInput = '';
      this.onSchemaChanged();
    }
  }

  removeEnumValue(field: FieldDefinition, idx: number) {
    field.enumValues.splice(idx, 1);
    this.onSchemaChanged();
  }

  onFieldChange() {
    this.onSchemaChanged();
  }

  onSchemaChanged() {
    this.schemaChange$.next();
  }

  // ── Schema serialization ─────────────────────────────────────────────────

  fieldsToSchemaJson(): any {
    const schema: any = {};
    for (const f of this.fields) {
      if (!f.name.trim()) continue;
      const def: any = {};
      if (f.hint) def.description = f.hint;

      switch (f.type) {
        case 'text':
          def.type = 'string';
          break;
        case 'categorical':
          def.type = 'string';
          if (f.enumValues.length > 0) def.enum = [...f.enumValues];
          break;
        case 'boolean':
          def.type = 'boolean';
          break;
        case 'number':
          def.type = 'number';
          if (f.minimum !== null && f.minimum !== undefined) def.minimum = f.minimum;
          if (f.maximum !== null && f.maximum !== undefined) def.maximum = f.maximum;
          break;
        case 'date':
          def.type = 'string';
          def.format = 'date';
          break;
      }
      schema[f.name.trim()] = def;
    }
    return schema;
  }

  schemaJsonToFields(schema: any): FieldDefinition[] {
    return Object.entries(schema).map(([name, def]: [string, any]) => {
      const f: FieldDefinition = {
        name,
        type: 'text',
        hint: def.description || '',
        enumValues: [],
        minimum: def.minimum ?? null,
        maximum: def.maximum ?? null,
        _enumInput: ''
      };
      if (def.format === 'date') {
        f.type = 'date';
      } else if (def.type === 'boolean') {
        f.type = 'boolean';
      } else if (def.type === 'number') {
        f.type = 'number';
      } else if (def.enum) {
        f.type = 'categorical';
        f.enumValues = def.enum;
      } else {
        f.type = 'text';
      }
      return f;
    });
  }

  // ── Save ─────────────────────────────────────────────────────────────────

  async saveSchema() {
    const schema = this.fieldsToSchemaJson();
    if (Object.keys(schema).length === 0) {
      this.toastr.warning('Add at least one field before saving.');
      return;
    }
    this.saving = true;
    try {
      await this.extractionService.saveSchema(this.sessionId, JSON.stringify(schema));
      this.toastr.success('Schema saved.');
    } catch (e) {
      this.toastr.error('Failed to save schema.');
    } finally {
      this.saving = false;
    }
  }

  // ── AI field suggestion ──────────────────────────────────────────────────

  async suggestFields() {
    this.suggesting = true;
    try {
      const suggestions = await this.extractionService.suggestFields(this.sessionId);
      if (!suggestions || suggestions.length === 0) {
        this.toastr.info('No suggestions returned by the AI.');
        return;
      }
      const existing = new Set(this.fields.map(f => f.name));
      for (const s of suggestions) {
        if (!existing.has(s.name)) {
          this.fields.push({
            name: s.name,
            type: s.type || 'text',
            hint: s.hint || '',
            enumValues: s.enum_values || [],
            minimum: s.minimum ?? null,
            maximum: s.maximum ?? null,
            _enumInput: ''
          });
          existing.add(s.name);
        }
      }
      this.toastr.success(`${suggestions.length} field suggestions added.`);
      this.onSchemaChanged();
    } catch (e) {
      this.toastr.error('AI field suggestion failed. Is the LLM server running?');
    } finally {
      this.suggesting = false;
    }
  }

  // ── Live preview ─────────────────────────────────────────────────────────

  setupPreviewDebounce() {
    const sub = this.schemaChange$
      .pipe(debounceTime(400))
      .subscribe(() => this.runPreview());
    this.subs.push(sub);
  }

  async loadCaseText() {
    if (!this.selectedCaseId) return;
    try {
      const data = await this.extractionService.getCaseText(this.selectedCaseId);
      this.reportText = data.full_text;
      this.highlightedReportHtml = this.escapeHtml(this.reportText);
    } catch {
      this.reportText = '';
      this.highlightedReportHtml = '';
    }
  }

  onCaseChange() {
    this.previewResult = null;
    this.previewError = null;
    this.loadCaseText();
    this.runPreview();
  }

  runPreview() {
    const schema = this.fieldsToSchemaJson();
    if (Object.keys(schema).length === 0 || !this.selectedCaseId) {
      this.previewResult = null;
      return;
    }
    this.previewLoading = true;
    this.previewError = null;

    if (this.previewSub) this.previewSub.unsubscribe();

    this.previewSub = this.extractionService
      .previewExtraction(this.sessionId, this.selectedCaseId, schema)
      .pipe(
        catchError(err => {
          this.previewError = 'Preview failed. Check that the LLM server is running.';
          this.previewLoading = false;
          return of(null);
        })
      )
      .subscribe(result => {
        this.previewLoading = false;
        if (!result) return;
        this.previewResult = result;
        this.updateHighlights(result);
      });
  }

  updateHighlights(result: any) {
    let html = this.escapeHtml(this.reportText);
    if (!result?.extracted_fields) {
      this.highlightedReportHtml = html;
      return;
    }
    // Collect all provenance spans
    const snippets: string[] = [];
    for (const key of Object.keys(result.extracted_fields)) {
      const prov = result.extracted_fields[key]?.provenance;
      if (prov) snippets.push(prov);
    }
    // Highlight unique snippets (longest first to avoid partial replacements)
    const sorted = [...new Set(snippets)].sort((a, b) => b.length - a.length);
    for (const snippet of sorted) {
      const escaped = this.escapeHtml(snippet);
      html = html.replace(escaped, `<mark class="prov-highlight">${escaped}</mark>`);
    }
    this.highlightedReportHtml = html;
  }

  escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  previewFields(): string[] {
    return this.previewResult ? Object.keys(this.previewResult.extracted_fields) : [];
  }

  confidenceClass(confidence: number | null): string {
    if (confidence === null || confidence === undefined) return 'text-muted';
    if (confidence >= 0.8) return 'text-success';
    if (confidence >= 0.5) return 'text-warning';
    return 'text-danger';
  }

  confidenceIcon(confidence: number | null): string {
    if (confidence === null || confidence === undefined) return 'bi-dash-circle';
    if (confidence >= 0.8) return 'bi-check-circle-fill';
    if (confidence >= 0.5) return 'bi-exclamation-circle-fill';
    return 'bi-x-circle-fill';
  }

  // ── Run extraction ───────────────────────────────────────────────────────

  async runExtraction() {
    const schema = this.fieldsToSchemaJson();
    if (Object.keys(schema).length === 0) {
      this.toastr.warning('Define at least one field first.');
      return;
    }
    // Save schema first
    await this.saveSchema();
    try {
      await this.extractionService.startExtraction(this.sessionId);
      this.toastr.success('Extraction started! Check the Review tab for progress.');
      this.router.navigate(['/extraction/review', this.sessionId]);
    } catch (e: any) {
      this.toastr.error(e?.error?.detail || 'Failed to start extraction.');
    }
  }

  // ── Load from saved search ───────────────────────────────────────────────

  async openSearchPicker() {
    if (this.savedSearches.length === 0) {
      try {
        const result: any = await this.savedSearchContentService.getDropdown(1, 100);
        this.savedSearches = result?.data ?? [];
      } catch {
        this.toastr.error('Failed to load saved searches.');
        return;
      }
    }
    this.selectedSearchId = this.savedSearches.length > 0 ? this.savedSearches[0].value : null;
    this.showSearchPicker = true;
  }

  async loadFromSavedSearch() {
    if (!this.selectedSearchId) return;
    this.loadingFromSearch = true;
    try {
      this.queuedCases = await this.extractionService.addFromSavedSearch(this.sessionId, this.selectedSearchId) ?? [];
      if (this.queuedCases.length > 0 && !this.selectedCaseId) {
        this.selectedCaseId = this.queuedCases[0].CaseId;
        this.loadCaseText();
      }
      this.toastr.success(`${this.queuedCases.length} case(s) in queue after loading saved search.`);
      this.showSearchPicker = false;
    } catch (e: any) {
      this.toastr.error(e?.error?.detail || 'Failed to load cases from saved search.');
    } finally {
      this.loadingFromSearch = false;
    }
  }

  get selectedCaseIndex(): number {
    return this.previewCasesShown.findIndex(c => c.CaseId === this.selectedCaseId);
  }

  stepCase(direction: -1 | 1) {
    const idx = this.selectedCaseIndex + direction;
    if (idx < 0 || idx >= this.previewCasesShown.length) return;
    this.selectedCaseId = this.previewCasesShown[idx].CaseId;
    this.onCaseChange();
  }

  get previewCasesShown(): any[] {
    return this.queuedCases.slice(0, 5);
  }
}
