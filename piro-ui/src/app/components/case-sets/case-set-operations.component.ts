import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {
  CaseSetOperationCreate, CaseSetOperationInput, CaseSetOperationPreview, CaseSetService,
  MembershipPolicy, SetOperation, caseSetError
} from '../../services/case-set.service';

@Component({standalone: false, selector: 'app-case-set-operations',
  templateUrl: './case-set-operations.component.html', styleUrls: ['./case-sets.css']})
export class CaseSetOperationsComponent implements OnInit {
  sources: {id: number; name: string}[] = [];
  leftSetId: number | null = null; rightSetId: number | null = null;
  operation: SetOperation = 'UNION'; membership: MembershipPolicy = 'NOT_EXCLUDED';
  name = ''; description = ''; busy = false; error = '';
  preview: CaseSetOperationPreview | null = null;
  private pendingCreate: CaseSetOperationCreate | null = null;
  readonly operations: {value: SetOperation; label: string; description: string}[] = [
    {value: 'UNION', label: 'Addition / Union (A ∪ B)', description: 'Cases in A or B, with each case appearing once.'},
    {value: 'INTERSECTION', label: 'Intersection (A ∩ B)', description: 'Only cases present in both A and B.'},
    {value: 'DIFFERENCE', label: 'Subtract B from A (A − B)', description: 'Cases in A with any cases present in B removed.'},
    {value: 'SYMMETRIC_DIFFERENCE', label: 'Symmetric difference (A △ B)', description: 'Cases in either A or B, excluding cases present in both.'}
  ];
  constructor(private api: CaseSetService, private router: Router) {}
  async ngOnInit() { await this.loadSources(); }
  get explanation() { return this.operations.find(o => o.value === this.operation)?.description; }
  private input(): CaseSetOperationInput {
    return {leftSetId: Number(this.leftSetId), rightSetId: Number(this.rightSetId),
      operation: this.operation, membership: this.membership};
  }
  invalidate() { this.preview = null; this.pendingCreate = null; this.error = ''; }
  swap() {
    [this.leftSetId, this.rightSetId] = [this.rightSetId, this.leftSetId];
    this.invalidate();
  }
  async loadSources() {
    if (this.busy) return;
    this.busy = true; this.invalidate();
    try {
      this.sources = await this.api.operationSources();
      if (!this.sources.some(s => s.id === this.leftSetId)) this.leftSetId = null;
      if (!this.sources.some(s => s.id === this.rightSetId)) this.rightSetId = null;
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
  async previewOperation() {
    if (this.busy || !this.leftSetId || !this.rightSetId) return;
    this.busy = true; this.invalidate();
    try { this.preview = await this.api.previewOperation(this.input()); }
    catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
  async save() {
    if (this.busy || !this.preview || !this.name.trim()) return;
    this.busy = true; this.error = '';
    const draft = {...this.input(), name: this.name.trim(), description: this.description,
      leftRevision: this.preview.left.revision, rightRevision: this.preview.right.revision};
    if (!this.pendingCreate || JSON.stringify({...this.pendingCreate, operationId: undefined}) !== JSON.stringify(draft)) {
      this.pendingCreate = {...draft, operationId: crypto.randomUUID()};
    }
    try {
      const result = await this.api.createOperation(this.pendingCreate);
      await this.router.navigate(['/case-sets', result.caseSetId]);
    } catch (error: any) {
      if (error?.status === 409) { this.preview = null; this.pendingCreate = null; }
      this.error = caseSetError(error);
    } finally { this.busy = false; }
  }
}
