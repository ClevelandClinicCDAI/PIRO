import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import {
  CytologyEvaluation,
  CytologyEvaluationSavePayload,
  CytologyTerminology,
  UserSearchResult
} from '../models/cytology-evaluation';

@Injectable({
  providedIn: 'root'
})
export class CytologyEvaluationService {
  private baseUrl = environment.apiBaseUrl + environment.cytologyEvaluationUrl;
  private userSearchUrl = environment.apiBaseUrl + environment.userSearchUrl;

  constructor(private http: HttpClient) {}

  getTerminology() {
    return new Promise((resolve) => {
      this.http.get<CytologyTerminology>(`${this.baseUrl}/terminology`).subscribe({
        next: (res: CytologyTerminology) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  create(payload: CytologyEvaluationSavePayload) {
    return new Promise((resolve) => {
      this.http.post<CytologyEvaluation>(this.baseUrl, payload).subscribe({
        next: (res: CytologyEvaluation) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  list() {
    return new Promise((resolve) => {
      this.http.get<CytologyEvaluation[]>(this.baseUrl).subscribe({
        next: (res: CytologyEvaluation[]) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: [], err })
      });
    });
  }

  get(evaluationId: number) {
    return new Promise((resolve) => {
      this.http.get<CytologyEvaluation>(`${this.baseUrl}/${evaluationId}`).subscribe({
        next: (res: CytologyEvaluation) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  save(evaluationId: number, payload: CytologyEvaluationSavePayload) {
    return new Promise((resolve) => {
      this.http.put<CytologyEvaluation>(`${this.baseUrl}/${evaluationId}`, payload).subscribe({
        next: (res: CytologyEvaluation) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  prelimVerify(evaluationId: number) {
    return new Promise((resolve) => {
      this.http.post<CytologyEvaluation>(`${this.baseUrl}/${evaluationId}/prelim-verify`, {}).subscribe({
        next: (res: CytologyEvaluation) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  finalVerify(evaluationId: number) {
    return new Promise((resolve) => {
      this.http.post<CytologyEvaluation>(`${this.baseUrl}/${evaluationId}/final-verify`, {}).subscribe({
        next: (res: CytologyEvaluation) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: null, err })
      });
    });
  }

  delete(evaluationId: number) {
    return new Promise((resolve) => {
      this.http.delete(`${this.baseUrl}/${evaluationId}`).subscribe({
        next: () => resolve({ status: true }),
        error: (err: any) => resolve({ status: false, err })
      });
    });
  }

  listCompleted() {
    return new Promise((resolve) => {
      this.http.get<CytologyEvaluation[]>(`${this.baseUrl}/completed`).subscribe({
        next: (res: CytologyEvaluation[]) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: [], err })
      });
    });
  }

  searchUsers(query: string) {
    return new Promise((resolve) => {
      this.http.get<UserSearchResult[]>(this.userSearchUrl, { params: { q: query } }).subscribe({
        next: (res: UserSearchResult[]) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, data: [], err })
      });
    });
  }
}
