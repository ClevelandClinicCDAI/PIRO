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
    this.startTicker();
  }

  ngOnDestroy(): void {
    this.stopStatusPoll();
    this.stopTicker();
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

  parseJsonValue(jsonStr: string | null): any {
    if (jsonStr === null || jsonStr === undefined) return null;
    try {
      return JSON.parse(jsonStr);
    } catch {
      return jsonStr;
    }
  }

  // ── Correct / Incorrect marking ───────────────────────────────────────────

  async markPrediction(cell: GridCell, event: Event) {
    event.stopPropagation();
    // Toggle: clicking again on an already-marked-incorrect cell reverts it back to default (assumed correct)
    const isTogglingOff = cell.isReviewed && cell.isIncorrect;
    const nextReviewed = !isTogglingOff;
    const nextIncorrect = !isTogglingOff;

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
        const data = await this.extractionService.getCaseText(caseId, this.sessionId);
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

  exportExcel() {
    this.extractionService.exportResults(this.sessionId, 'excel').subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extraction_${this.sessionId}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // ── Status polling ────────────────────────────────────────────────────────

  startStatusPoll() {
    const poll = async () => {
      try {
        this.statusInfo = await this.extractionService.getStatus(this.sessionId);
        if (this.statusInfo?.status === 'running') {
          await this.loadResults();
        } else {
          this.stopStatusPoll();
        }
      } catch { }
    };
    poll();
    this.pollInterval = setInterval(poll, 4000);
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

  // ── Progress monitoring (elapsed time / ETA / stall detection) ───────────

  private tickInterval: any = null;
  now = Date.now();

  private startTicker() {
    if (this.tickInterval) return;
    this.tickInterval = setInterval(() => { this.now = Date.now(); }, 1000);
  }

  private stopTicker() {
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }
  }

  private formatDuration(ms: number): string {
    if (ms < 0) ms = 0;
    const totalSeconds = Math.floor(ms / 1000);
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  }

  get elapsedText(): string | null {
    const startedAt = this.statusInfo?.started_at;
    if (!startedAt) return null;
    const end = this.statusInfo?.completed_at ? new Date(this.statusInfo.completed_at).getTime() : this.now;
    return this.formatDuration(end - new Date(startedAt).getTime());
  }

  get etaText(): string | null {
    if (!this.isRunning || !this.statusInfo?.started_at) return null;
    const completed = this.statusInfo.completed ?? 0;
    const total = this.statusInfo.total ?? 0;
    if (completed <= 0 || total <= completed) return null;
    const elapsedMs = this.now - new Date(this.statusInfo.started_at).getTime();
    const msPerCase = elapsedMs / completed;
    const remainingMs = msPerCase * (total - completed);
    return this.formatDuration(remainingMs);
  }

  get lastUpdatedAgoText(): string | null {
    const lastUpdated = this.statusInfo?.last_updated_at;
    if (!lastUpdated) return null;
    return this.formatDuration(this.now - new Date(lastUpdated).getTime());
  }

  // Flag a run as possibly stalled if no case has progressed in far longer
  // than cases have actually been taking so far in this run. The LLM backend
  // here is Azure OpenAI (GPT-5.4) — a fast hosted API where each case
  // normally finishes in well under the client's 120s per-call timeout — so
  // a real stall (crashed job, hung request, rate-limit backoff) should be
  // caught quickly rather than waiting a long time to flag it.
  get isStalled(): boolean {
    if (!this.isRunning) return false;
    const lastUpdated = this.statusInfo?.last_updated_at ?? this.statusInfo?.started_at;
    if (!lastUpdated) return false;
    const sinceLastUpdateMs = this.now - new Date(lastUpdated).getTime();

    const FLOOR_MS = 5 * 60 * 1000; // never flag before 5 minutes of silence
    let threshold = FLOOR_MS;

    const completed = this.statusInfo?.completed ?? 0;
    const startedAt = this.statusInfo?.started_at ? new Date(this.statusInfo.started_at).getTime() : null;
    if (completed > 0 && startedAt) {
      const avgMsPerCase = (this.now - startedAt) / completed;
      threshold = Math.max(FLOOR_MS, avgMsPerCase * 6);
    }

    return sinceLastUpdateMs > threshold;
  }
}
