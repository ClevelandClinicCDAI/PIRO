import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ExtractionService {

  constructor(private http: HttpClient) {}

  // Computed per-call (not at module load) so it picks up the apiBaseUrl
  // set at runtime by AppConfigService via APP_INITIALIZER.
  private get BASE(): string {
    return environment.apiBaseUrl + 'extraction/';
  }

  // ── Sessions ──────────────────────────────────────────────────────────────

  createSession(name: string, schemaJson?: string): Promise<any> {
    return this.http.post<any>(this.BASE + 'session', { name, schema_definition: schemaJson ?? null })
      .toPromise();
  }

  getSessions(): Promise<any[]> {
    return this.http.get<any[]>(this.BASE + 'sessions').toPromise() as Promise<any[]>;
  }

  getSession(sessionId: number): Promise<any> {
    return this.http.get<any>(`${this.BASE}session/${sessionId}`).toPromise();
  }

  saveSchema(sessionId: number, schemaJson: string, name?: string): Promise<any> {
    const body: any = { schema_definition: schemaJson };
    if (name) body.name = name;
    return this.http.put<any>(`${this.BASE}schema/${sessionId}`, body).toPromise();
  }

  deleteSession(sessionId: number): Promise<any> {
    return this.http.delete<any>(`${this.BASE}session/${sessionId}`).toPromise();
  }

  // ── Queue ─────────────────────────────────────────────────────────────────

  addToQueue(sessionId: number, caseIds: number[]): Promise<any[]> {
    return this.http.post<any[]>(this.BASE + 'queue', { session_id: sessionId, case_ids: caseIds })
      .toPromise() as Promise<any[]>;
  }

  getQueue(sessionId: number): Promise<any[]> {
    return this.http.get<any[]>(`${this.BASE}queue/${sessionId}`).toPromise() as Promise<any[]>;
  }

  addFromSavedSearch(sessionId: number, searchId: number): Promise<any[]> {
    return this.http.post<any[]>(this.BASE + 'queue/from-saved-search', { session_id: sessionId, search_id: searchId })
      .toPromise() as Promise<any[]>;
  }

  removeFromQueue(sessionId: number, caseId: number): Promise<any> {
    return this.http.delete<any>(`${this.BASE}queue/${sessionId}/${caseId}`).toPromise();
  }

  // ── Extraction run ────────────────────────────────────────────────────────

  startExtraction(sessionId: number, runType: 'validation' | 'full' = 'full', validationSize?: number): Promise<any> {
    const body: any = { session_id: sessionId, run_type: runType };
    if (runType === 'validation' && validationSize) body.validation_size = validationSize;
    return this.http.post<any>(this.BASE + 'run', body).toPromise();
  }

  getStatus(sessionId: number): Promise<any> {
    return this.http.get<any>(`${this.BASE}status/${sessionId}`).toPromise();
  }

  // ── Results ───────────────────────────────────────────────────────────────

  getResults(sessionId: number): Promise<any[]> {
    return this.http.get<any[]>(`${this.BASE}results/${sessionId}`).toPromise() as Promise<any[]>;
  }

  patchResult(resultId: number, reviewedValue?: string, isReviewed?: boolean, isIncorrect?: boolean): Promise<any> {
    const body: any = {};
    if (reviewedValue !== undefined) body.reviewed_value = reviewedValue;
    if (isReviewed !== undefined) body.is_reviewed = isReviewed;
    if (isIncorrect !== undefined) body.is_incorrect = isIncorrect;
    return this.http.patch<any>(`${this.BASE}results/${resultId}`, body).toPromise();
  }

  approveAllHighConfidence(sessionId: number, threshold: number = 0.8): Promise<any> {
    return this.http.post<any>(`${this.BASE}results/${sessionId}/approve-all?threshold=${threshold}`, {})
      .toPromise();
  }

  getLowConfidenceCases(sessionId: number, threshold = 0.8): Promise<{case_ids: number[], count: number}> {
    return this.http.get<any>(`${this.BASE}results/${sessionId}/low-confidence-cases?threshold=${threshold}`).toPromise();
  }

  getIncorrectCases(sessionId: number): Promise<{case_ids: number[], count: number}> {
    return this.http.get<any>(`${this.BASE}results/${sessionId}/incorrect-cases`).toPromise();
  }

  // ── Export ────────────────────────────────────────────────────────────────

  exportResults(sessionId: number, format: 'csv' | 'json' | 'excel' = 'csv'): Observable<Blob> {
    const mime = format === 'excel'
      ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      : format === 'json' ? 'application/json' : 'text/csv';
    return this.http.get(`${this.BASE}export/${sessionId}?format=${format}`, {
      responseType: 'blob'
    });
  }

  // ── AI helpers ────────────────────────────────────────────────────────────

  suggestFields(sessionId?: number, sampleText?: string): Promise<any[]> {
    const body: any = {};
    if (sessionId) body.session_id = sessionId;
    if (sampleText) body.sample_text = sampleText;
    return this.http.post<any[]>(this.BASE + 'suggest-fields', body).toPromise() as Promise<any[]>;
  }

  previewExtraction(sessionId: number, caseId: number, schema: any): Observable<any> {
    return this.http.post<any>(this.BASE + 'preview', {
      session_id: sessionId,
      case_id: caseId,
      extraction_schema: schema
    });
  }

  // ── Case text ─────────────────────────────────────────────────────────────

  getCaseText(caseId: number): Promise<any> {
    return this.http.get<any>(`${this.BASE}case/${caseId}/text`).toPromise();
  }
}
