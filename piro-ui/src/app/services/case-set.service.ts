import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

export type ReviewState = 'UNREVIEWED' | 'INCLUDED' | 'EXCLUDED';
export type ReviewFilter = 'ALL' | ReviewState;
export interface CaseSetSummary {
  caseSetId: number; name: string; description: string;
  sourceType: 'SAVED_SEARCH' | 'COHORT' | 'OPERATION' | 'MANUAL'; sourceId: number; sourceName: string;
  archived: boolean; revision: number; createdAt: string; updatedAt: string;
  isPublic: boolean; specialtyCategory: string | null;
  captureState: 'CAPTURING' | 'READY' | 'FAILED'; captureCursor: string;
  captureExpected: number | null; captureSeen: number; captureError: string;
  captureFinishedAt: string | null; lastCaseId: number | null; reviewFilter: ReviewFilter;
  total: number; unreviewed: number; included: number; excluded: number;
}
export interface CaseSetMember {
  caseId: number; ordinal: number; state: ReviewState; reviewedAt: string | null;
  revision: number; unavailable: boolean; summary: any;
}
export interface CaseSetSpecimen {
  specimenId: number; part: string; selected: boolean; available: boolean;
}
export interface CaseSetSpecimens {
  specimens: CaseSetSpecimen[]; member: Partial<CaseSetMember>; set: CaseSetSummary;
}
export interface CaseSetPage {
  items: CaseSetMember[]; total: number; page: number; size: number;
  filter: ReviewFilter; set: CaseSetSummary;
}
export interface CaseSetSources {
  searches: {id: number; name: string}[]; cohorts: {id: number; name: string}[];
}
export interface CaseSetCreate {
  name: string; description: string; sourceType: 'SAVED_SEARCH' | 'COHORT';
  sourceId: number; operationId: string;
}
export interface CaseSetCartCreate {
  name: string; description: string; caseIds: number[]; operationId: string;
}
export interface TeachingSetSummary {
  caseSetId: number; name: string; description: string; specialtyCategory: string;
  creatorName: string; total: number; createdAt: string; updatedAt: string;
}
export interface TeachingCase {
  caseId: number; ordinal: number; unavailable: boolean; summary: any;
}
export interface TeachingSetPage {
  items: TeachingCase[]; total: number; page: number; size: number; set: TeachingSetSummary;
}
export type SetOperation = 'UNION' | 'INTERSECTION' | 'DIFFERENCE' | 'SYMMETRIC_DIFFERENCE';
export type MembershipPolicy = 'NOT_EXCLUDED' | 'INCLUDED_ONLY';
export interface CaseSetOperationInput {
  leftSetId: number; rightSetId: number; operation: SetOperation; membership: MembershipPolicy;
}
export interface OperationOperand {
  id: number; name: string; revision: number; eligible: number;
  total: number; included: number; unreviewed: number; excluded: number;
}
export interface CaseSetOperationPreview {
  left: OperationOperand; right: OperationOperand; total: number;
  operation: SetOperation; membership: MembershipPolicy;
}
export interface CaseSetOperationCreate extends CaseSetOperationInput {
  name: string; description: string; leftRevision: number; rightRevision: number; operationId: string;
}

export function caseSetError(error: any): string {
  if (error?.status === 0) return 'PIRO could not be reached. Check your connection and retry.';
  const detail = error?.error?.detail;
  return typeof detail === 'string' ? detail : 'The action could not be completed. Please retry.';
}

@Injectable({providedIn: 'root'})
export class CaseSetService {
  private readonly base = environment.apiBaseUrl + 'case-sets';
  constructor(private http: HttpClient) {}
  sources() { return firstValueFrom(this.http.get<CaseSetSources>(`${this.base}/sources`)); }
  specialtyCategories() { return firstValueFrom(this.http.get<string[]>(`${this.base}/specialty-categories`)); }
  share(set: CaseSetSummary, isPublic: boolean, specialtyCategory: string | null) {
    return firstValueFrom(this.http.put<CaseSetSummary>(`${this.base}/${set.caseSetId}/sharing`,
      {isPublic, specialtyCategory, revision: set.revision}));
  }
  teachingSets(specialty: string, page: number) {
    return firstValueFrom(this.http.get<{items: TeachingSetSummary[]; total: number; page: number; size: number; categories: string[]}>(
      environment.apiBaseUrl + 'teaching-sets', {params: {specialty, page, size: 25}}));
  }
  teachingCases(id: number, page: number) {
    return firstValueFrom(this.http.get<TeachingSetPage>(environment.apiBaseUrl + `teaching-sets/${id}/cases`, {params: {page, size: 1}}));
  }
  list(archived: boolean, page: number) {
    return firstValueFrom(this.http.get<{items: CaseSetSummary[]; total: number}>(this.base, {params: {archived, page, size: 25}}));
  }
  create(payload: CaseSetCreate) { return firstValueFrom(this.http.post<CaseSetSummary>(this.base, payload)); }
  cartTargets() {
    return firstValueFrom(this.http.get<{id: number; name: string}[]>(`${this.base}/cart/targets`));
  }
  createFromCart(payload: CaseSetCartCreate) {
    return firstValueFrom(this.http.post<CaseSetSummary>(`${this.base}/from-cart`, payload));
  }
  addCases(id: number, caseIds: number[]) {
    return firstValueFrom(this.http.post<{set: CaseSetSummary; added: number; alreadyPresent: number}>(
      `${this.base}/${id}/cases`, {caseIds}));
  }
  operationSources() {
    return firstValueFrom(this.http.get<{id: number; name: string}[]>(`${this.base}/operations/sources`));
  }
  previewOperation(payload: CaseSetOperationInput) {
    return firstValueFrom(this.http.post<CaseSetOperationPreview>(`${this.base}/operations/preview`, payload));
  }
  createOperation(payload: CaseSetOperationCreate) {
    return firstValueFrom(this.http.post<CaseSetSummary>(`${this.base}/operations`, payload));
  }
  detail(id: number) { return firstValueFrom(this.http.get<CaseSetSummary>(`${this.base}/${id}`)); }
  capture(set: CaseSetSummary) {
    return firstValueFrom(this.http.post<CaseSetSummary>(`${this.base}/${set.caseSetId}/capture`, {cursor: set.captureCursor}));
  }
  edit(set: CaseSetSummary, name: string, description: string, archived: boolean) {
    return firstValueFrom(this.http.put<CaseSetSummary>(`${this.base}/${set.caseSetId}`, {name, description, archived, revision: set.revision}));
  }
  delete(set: CaseSetSummary) {
    return firstValueFrom(this.http.delete<void>(`${this.base}/${set.caseSetId}`, {params: {revision: set.revision}}));
  }
  members(id: number, filter: ReviewFilter, page: number, size: number, resume = false) {
    return firstValueFrom(this.http.get<CaseSetPage>(`${this.base}/${id}/cases`, {params: {filter, page, size, resume}}));
  }
  decide(id: number, member: CaseSetMember, state: ReviewState) {
    return firstValueFrom(this.http.put<{set: CaseSetSummary; member: Partial<CaseSetMember>}>(
      `${this.base}/${id}/cases/${member.caseId}`, {state, revision: member.revision}));
  }
  specimens(id: number, caseId: number) {
    return firstValueFrom(this.http.get<CaseSetSpecimens>(`${this.base}/${id}/cases/${caseId}/specimens`));
  }
  selectSpecimens(id: number, member: CaseSetMember, specimenIds: number[]) {
    return firstValueFrom(this.http.put<CaseSetSpecimens>(`${this.base}/${id}/cases/${member.caseId}/specimens`,
      {specimenIds, revision: member.revision}));
  }
  position(id: number, caseId: number | null, filter: ReviewFilter) {
    return firstValueFrom(this.http.put(`${this.base}/${id}/position`, {caseId, filter}));
  }
}
