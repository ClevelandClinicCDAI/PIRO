import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

const BASE = environment.apiBaseUrl + 'extraction/';

@Injectable({
  providedIn: 'root'
})
export class ExtractionService {

  constructor(private http: HttpClient) {}

  // ── Sessions ──────────────────────────────────────────────────────────────

  createSession(name: string, schemaJson?: string): Promise<any> {
    return this.http.post<any>(BASE + 'session', { name, schema_definition: schemaJson ?? null })
      .toPromise();
  }

  getSessions(): Promise<any[]> {
    return this.http.get<any[]>(BASE + 'sessions').toPromise() as Promise<any[]>;
  }

  getSession(sessionId: number): Promise<any> {
    return this.http.get<any>(`${BASE}session/${sessionId}`).toPromise();
  }

  saveSchema(sessionId: number, schemaJson: string, name?: string): Promise<any> {
    const body: any = { schema_definition: schemaJson };
    if (name) body.name = name;
    return this.http.put<any>(`${BASE}schema/${sessionId}`, body).toPromise();
  }

  deleteSession(sessionId: number): Promise<any> {
    return this.http.delete<any>(`${BASE}session/${sessionId}`).toPromise();
  }

  // ── Queue ─────────────────────────────────────────────────────────────────

  addToQueue(sessionId: number, caseIds: number[]): Promise<any[]> {
    return this.http.post<any[]>(BASE + 'queue', { session_id: sessionId, case_ids: caseIds })
      .toPromise() as Promise<any[]>;
  }

  getQueue(sessionId: number): Promise<any[]> {
    return this.http.get<any[]>(`${BASE}queue/${sessionId}`).toPromise() as Promise<any[]>;
  }

  removeFromQueue(sessionId: number, caseId: number): Promise<any> {
    return this.http.delete<any>(`${BASE}queue/${sessionId}/${caseId}`).toPromise();
  }

  // ── Extraction run ────────────────────────────────────────────────────────

  startExtraction(sessionId: number): Promise<any> {
    return this.http.post<any>(BASE + 'run', { session_id: sessionId }).toPromise();
  }

  getStatus(sessionId: number): Promise<any> {
    return this.http.get<any>(`${BASE}status/${sessionId}`).toPromise();
  }

  // ── Results ───────────────────────────────────────────────────────────────

  getResults(sessionId: number): Promise<any[]> {
    return this.http.get<any[]>(`${BASE}results/${sessionId}`).toPromise() as Promise<any[]>;
  }

  patchResult(resultId: number, reviewedValue?: string, isReviewed?: boolean): Promise<any> {
    const body: any = {};
    if (reviewedValue !== undefined) body.reviewed_value = reviewedValue;
    if (isReviewed !== undefined) body.is_reviewed = isReviewed;
    return this.http.patch<any>(`${BASE}results/${resultId}`, body).toPromise();
  }

  approveAllHighConfidence(sessionId: number, threshold: number = 0.8): Promise<any> {
    return this.http.post<any>(`${BASE}results/${sessionId}/approve-all?threshold=${threshold}`, {})
      .toPromise();
  }

  // ── Export ────────────────────────────────────────────────────────────────

  exportResults(sessionId: number, format: 'csv' | 'json' = 'csv'): Observable<Blob> {
    return this.http.get(`${BASE}export/${sessionId}?format=${format}`, {
      responseType: 'blob'
    });
  }

  // ── AI helpers ────────────────────────────────────────────────────────────

  suggestFields(sessionId?: number, sampleText?: string): Promise<any[]> {
    const body: any = {};
    if (sessionId) body.session_id = sessionId;
    if (sampleText) body.sample_text = sampleText;
    return this.http.post<any[]>(BASE + 'suggest-fields', body).toPromise() as Promise<any[]>;
  }

  previewExtraction(sessionId: number, caseId: number, schema: any): Observable<any> {
    return this.http.post<any>(BASE + 'preview', {
      session_id: sessionId,
      case_id: caseId,
      extraction_schema: schema
    });
  }

  // ── Case text ─────────────────────────────────────────────────────────────

  getCaseText(caseId: number): Promise<any> {
    return this.http.get<any>(`${BASE}case/${caseId}/text`).toPromise();
  }
}
