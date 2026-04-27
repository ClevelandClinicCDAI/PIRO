import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ExtractionService } from '../../../services/extraction.service';

interface GridRow {
  caseId: number;
  caseNumber: string;
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
  isIncorrect: boolean;
}

@Component({
  selector: 'app-extraction-review',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './extraction-review.component.html',
  styleUrls: ['./extraction-review.component.css']
})
export class ExtractionReviewComponent implements OnInit, OnDestroy {
  sessionId!: number;
  session: any = null;
  fields: string[] = [];
  rows: GridRow[] = [];

  // Stable insertion-order tracking — cases stay in the order they first appear.
  // Subsequent polls update cells in place without reordering.
  private caseOrder: number[] = [];
  private caseRowMap = new Map<number, GridRow>();

  // Side panel
  selectedCell: GridCell | null = null;
  selectedCaseId: number | null = null;
  selectedCaseNumber: string | null = null;
  selectedField: string | null = null;
  reportSegments: { CommentType: string; CommentText: string; html: string }[] = [];
  reportText = '';   // kept for provenance search
  sidePanelLoading = false;

  // Status polling
  statusInfo: any = null;
  private pollInterval: any = null;

  loading = true;
  approving = false;
  runningFull = false;
  refiningLowConf = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
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

    // Determine field order from schema (only set once)
    if (this.fields.length === 0 && this.session?.SchemaJson) {
      try {
        this.fields = Object.keys(JSON.parse(this.session.SchemaJson));
      } catch { }
    }
    if (this.fields.length === 0 && results.length > 0) {
      this.fields = [...new Set(results.map((r: any) => r.FieldName))];
    }

    // Update cells in place; append new cases in arrival order.
    // This prevents reordering as results stream in during a run.
    for (const r of results) {
      if (!this.caseRowMap.has(r.CaseId)) {
        const newRow: GridRow = { caseId: r.CaseId, caseNumber: r.CaseNumber ?? String(r.CaseId), cells: {} };
        this.caseOrder.push(r.CaseId);
        this.caseRowMap.set(r.CaseId, newRow);
      }
      const row = this.caseRowMap.get(r.CaseId)!;
      const displayValue = this.parseJsonValue(r.ExtractedValue);
      row.cells[r.FieldName] = {
        resultId: r.ExtractionResultId,
        extractedValue: this.parseJsonValue(r.ExtractedValue),
        reviewedValue: this.parseJsonValue(r.ReviewedValue),
        displayValue,
        confidence: r.Confidence,
        provenanceText: r.ProvenanceText,
        isReviewed: r.IsReviewed,
        isIncorrect: r.IsIncorrect ?? false,
      };
    }

    this.rows = this.caseOrder.map(id => this.caseRowMap.get(id)!);
  }

  private resetResultState() {
    this.caseOrder = [];
    this.caseRowMap.clear();
    this.rows = [];
    this.fields = [];
  }

  parseJsonValue(jsonStr: string | null): any {
    if (jsonStr === null || jsonStr === undefined) return null;
    try {
      return JSON.parse(jsonStr);
    } catch {
      return jsonStr;
    }
  }

  // ── Correct / Incorrect marking ───────────────────────────────────────────

  async markPrediction(cell: GridCell, correct: boolean, event: Event) {
    event.stopPropagation();
    // Toggle off if clicking the already-active verdict; otherwise apply new verdict
    const isTogglingOff = cell.isReviewed && (correct ? !cell.isIncorrect : cell.isIncorrect);
    const nextReviewed = !isTogglingOff;
    const nextIncorrect = !isTogglingOff ? !correct : false;

    try {
      await this.extractionService.patchResult(cell.resultId, undefined, nextReviewed, nextIncorrect);
      cell.isReviewed = nextReviewed;
      cell.isIncorrect = nextIncorrect;
    } catch {
      this.toastr.error('Failed to save.');
    }
  }

  // ── Confidence styling ────────────────────────────────────────────────────

  cellClass(cell: GridCell | undefined): string {
    if (!cell) return '';
    if (cell.isReviewed && cell.isIncorrect) return 'cell-incorrect';
    if (cell.isReviewed && !cell.isIncorrect) return 'cell-correct';
    if (cell.confidence === null || cell.confidence === undefined) return '';
    if (cell.confidence >= 0.8) return 'cell-high';
    if (cell.confidence >= 0.5) return 'cell-medium';
    return 'cell-low';
  }

  // ── Side panel ────────────────────────────────────────────────────────────

  async selectCell(cell: GridCell | undefined, caseId: number, caseNumber: string, field: string) {
    if (!cell) return;
    const previousCaseId = this.selectedCaseId;
    this.selectedCell = cell;
    this.selectedCaseId = caseId;
    this.selectedCaseNumber = caseNumber;
    this.selectedField = field;

    if (this.reportText === '' || previousCaseId !== caseId) {
      this.sidePanelLoading = true;
      try {
        const data = await this.extractionService.getCaseText(caseId);
        this.reportText = data.full_text ?? '';
        this.reportSegments = (data.segments ?? []).map((s: any) => ({
          CommentType: s.CommentType,
          CommentText: s.CommentText,
          html: ''
        }));
      } catch {
        this.reportText = 'Could not load report text.';
        this.reportSegments = [];
      } finally {
        this.sidePanelLoading = false;
      }
    }
    this.updateReportHtml(cell.provenanceText);
  }

  updateReportHtml(prov: string | null) {
    const escapedProv = prov ? this.escapeHtml(prov) : null;
    this.reportSegments = this.reportSegments.map(seg => {
      let text = this.escapeHtml(seg.CommentText).replace(/\|\|\|\|/g, '\n');
      if (escapedProv && text.includes(escapedProv)) {
        text = text.replace(escapedProv, `<mark class="prov-highlight">${escapedProv}</mark>`);
      }
      return { ...seg, html: text };
    });
  }

  escapeHtml(text: string): string {
    return (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  closePanel() {
    this.selectedCell = null;
    this.selectedCaseId = null;
    this.selectedCaseNumber = null;
    this.selectedField = null;
    this.reportSegments = [];
    this.reportText = '';
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

  // ── Refine on low-confidence ──────────────────────────────────────────────

  async refineOnIncorrect() {
    this.refiningLowConf = true;
    try {
      const res = await this.extractionService.getIncorrectCases(this.sessionId);
      if (!res || res.count === 0) {
        this.toastr.info('No incorrect cases found — mark predictions as incorrect first.');
        return;
      }
      this.router.navigate(
        ['/extraction/schema', this.sessionId],
        { queryParams: { mode: 'incorrect', caseIds: res.case_ids.join(',') } }
      );
    } catch (e: any) {
      this.toastr.error('Failed to load incorrect cases.');
    } finally {
      this.refiningLowConf = false;
    }
  }

  async runFullExtraction() {
    this.runningFull = true;
    try {
      await this.extractionService.startExtraction(this.sessionId, 'full');
      this.toastr.success('Full extraction started. Progress will appear below.');
      this.resetResultState();
      this.startStatusPoll();
    } catch (e: any) {
      this.toastr.error(e?.error?.detail || 'Failed to start full extraction.');
    } finally {
      this.runningFull = false;
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
