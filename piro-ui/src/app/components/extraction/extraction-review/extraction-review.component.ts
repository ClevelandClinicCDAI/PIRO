import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ExtractionService } from '../../../services/extraction.service';

interface GridRow {
  caseId: number;
  cells: { [fieldName: string]: GridCell };
}

interface GridCell {
  resultId: number;
  extractedValue: any;
  reviewedValue: any;
  displayValue: any;
  confidence: number | null;
  provenanceText: string | null;
  isReviewed: boolean;
  editing: boolean;
  editValue: string;
}

@Component({
  selector: 'app-extraction-review',
  templateUrl: './extraction-review.component.html',
  styleUrls: ['./extraction-review.component.css']
})
export class ExtractionReviewComponent implements OnInit, OnDestroy {
  sessionId!: number;
  session: any = null;
  fields: string[] = [];
  rows: GridRow[] = [];

  // Side panel
  selectedCell: GridCell | null = null;
  selectedCaseId: number | null = null;
  selectedField: string | null = null;
  reportText = '';
  reportHtml = '';
  sidePanelLoading = false;

  // Status polling
  statusInfo: any = null;
  private pollInterval: any = null;

  loading = true;
  approving = false;

  constructor(
    private route: ActivatedRoute,
    private extractionService: ExtractionService,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.sessionId = parseInt(this.route.snapshot.paramMap.get('id') || '0', 10);
    this.loadData();
    this.startStatusPoll();
  }

  ngOnDestroy(): void {
    this.stopStatusPoll();
  }

  async loadData() {
    this.loading = true;
    try {
      this.session = await this.extractionService.getSession(this.sessionId);
      await this.loadResults();
    } catch (e) {
      this.toastr.error('Failed to load results.');
    } finally {
      this.loading = false;
    }
  }

  async loadResults() {
    const results: any[] = await this.extractionService.getResults(this.sessionId) ?? [];

    // Determine field order from schema
    if (this.session?.SchemaJson) {
      try {
        this.fields = Object.keys(JSON.parse(this.session.SchemaJson));
      } catch { }
    }
    if (this.fields.length === 0 && results.length > 0) {
      this.fields = [...new Set(results.map((r: any) => r.FieldName))];
    }

    // Build grid rows
    const caseMap = new Map<number, GridRow>();
    for (const r of results) {
      if (!caseMap.has(r.CaseId)) {
        caseMap.set(r.CaseId, { caseId: r.CaseId, cells: {} });
      }
      const row = caseMap.get(r.CaseId)!;
      const displayValue = r.IsReviewed ? this.parseJsonValue(r.ReviewedValue) : this.parseJsonValue(r.ExtractedValue);
      row.cells[r.FieldName] = {
        resultId: r.ExtractionResultId,
        extractedValue: this.parseJsonValue(r.ExtractedValue),
        reviewedValue: this.parseJsonValue(r.ReviewedValue),
        displayValue,
        confidence: r.Confidence,
        provenanceText: r.ProvenanceText,
        isReviewed: r.IsReviewed,
        editing: false,
        editValue: String(displayValue ?? '')
      };
    }
    this.rows = Array.from(caseMap.values());
  }

  parseJsonValue(jsonStr: string | null): any {
    if (jsonStr === null || jsonStr === undefined) return null;
    try {
      return JSON.parse(jsonStr);
    } catch {
      return jsonStr;
    }
  }

  // ── Inline editing ────────────────────────────────────────────────────────

  startEdit(cell: GridCell) {
    cell.editing = true;
    cell.editValue = cell.displayValue !== null && cell.displayValue !== undefined
      ? String(cell.displayValue) : '';
  }

  async commitEdit(cell: GridCell) {
    cell.editing = false;
    const newValue = JSON.stringify(cell.editValue);
    try {
      await this.extractionService.patchResult(cell.resultId, newValue, true);
      cell.reviewedValue = cell.editValue;
      cell.displayValue = cell.editValue;
      cell.isReviewed = true;
    } catch {
      this.toastr.error('Failed to save edit.');
    }
  }

  cancelEdit(cell: GridCell) {
    cell.editing = false;
    cell.editValue = String(cell.displayValue ?? '');
  }

  // ── Confidence styling ────────────────────────────────────────────────────

  cellClass(cell: GridCell | undefined): string {
    if (!cell) return '';
    if (cell.isReviewed) return 'cell-reviewed';
    if (cell.confidence === null || cell.confidence === undefined) return '';
    if (cell.confidence >= 0.8) return 'cell-high';
    if (cell.confidence >= 0.5) return 'cell-medium';
    return 'cell-low';
  }

  // ── Side panel ────────────────────────────────────────────────────────────

  async selectCell(cell: GridCell | undefined, caseId: number, field: string) {
    if (!cell) return;
    this.selectedCell = cell;
    this.selectedCaseId = caseId;
    this.selectedField = field;

    if (this.reportText === '' || this.selectedCaseId !== caseId) {
      this.sidePanelLoading = true;
      try {
        const data = await this.extractionService.getCaseText(caseId);
        this.reportText = data.full_text;
      } catch {
        this.reportText = 'Could not load report text.';
      } finally {
        this.sidePanelLoading = false;
      }
    }
    this.updateReportHtml(cell.provenanceText);
  }

  updateReportHtml(prov: string | null) {
    let html = this.escapeHtml(this.reportText);
    if (prov) {
      const escapedProv = this.escapeHtml(prov);
      html = html.replace(escapedProv, `<mark class="prov-highlight">${escapedProv}</mark>`);
    }
    this.reportHtml = html;
  }

  escapeHtml(text: string): string {
    return (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  closePanel() {
    this.selectedCell = null;
    this.selectedCaseId = null;
    this.selectedField = null;
  }

  // ── Bulk approve ──────────────────────────────────────────────────────────

  async approveAll() {
    this.approving = true;
    try {
      const res = await this.extractionService.approveAllHighConfidence(this.sessionId, 0.8);
      this.toastr.success(`${res.approved_count} high-confidence results approved.`);
      await this.loadResults();
    } catch {
      this.toastr.error('Failed to bulk approve.');
    } finally {
      this.approving = false;
    }
  }

  // ── Export ────────────────────────────────────────────────────────────────

  exportCsv() {
    this.extractionService.exportResults(this.sessionId, 'csv').subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extraction_${this.sessionId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  exportJson() {
    this.extractionService.exportResults(this.sessionId, 'json').subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extraction_${this.sessionId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // ── Status polling ────────────────────────────────────────────────────────

  startStatusPoll() {
    this.pollInterval = setInterval(async () => {
      try {
        this.statusInfo = await this.extractionService.getStatus(this.sessionId);
        if (this.statusInfo?.status === 'running') {
          await this.loadResults();
        } else {
          this.stopStatusPoll();
        }
      } catch { }
    }, 4000);
  }

  stopStatusPoll() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  get progressPercent(): number {
    if (!this.statusInfo || this.statusInfo.total === 0) return 0;
    return Math.round((this.statusInfo.completed / this.statusInfo.total) * 100);
  }

  get isRunning(): boolean {
    return this.statusInfo?.status === 'running';
  }
}
