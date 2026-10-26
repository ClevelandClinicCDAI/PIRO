import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgModel } from '@angular/forms';
import { CaseSetMember, CaseSetService, CaseSetSpecimen, CaseSetSummary, ReviewFilter, ReviewState, caseSetError } from '../../services/case-set.service';

@Component({standalone: false, selector: 'app-case-set-review',
  templateUrl: './case-set-review.component.html', styleUrls: ['./case-sets.css']})
export class CaseSetReviewComponent implements OnInit, OnDestroy {
  id = 0; set: CaseSetSummary | null = null; items: CaseSetMember[] = [];
  filter: ReviewFilter = 'ALL'; page = 1; readonly size = 1; total = 0;
  selectedFilter: ReviewFilter = 'ALL';
  busy = false; capturing = false; pauseRequested = false; error = ''; saved = '';
  pendingCaseId: number | null = null;
  specimens: CaseSetSpecimen[] = [];
  specimenLoading = false; specimenSaving = false; specimenError = ''; specimenSaved = '';
  specimensLoaded = false;
  private destroyed = false;
  @ViewChild('caseContent') private caseContent?: ElementRef<HTMLElement>;
  @ViewChild('filterControl') private filterControl?: NgModel;
  constructor(private api: CaseSetService, private route: ActivatedRoute) {}
  async ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    await this.reload();
  }
  ngOnDestroy() { this.destroyed = true; this.pauseRequested = true; }
  get reviewed() { return this.set ? this.set.total - this.set.unreviewed : 0; }
  get progress() { return this.set?.total ? this.reviewed / this.set.total * 100 : 0; }
  get lastPage() { return Math.max(1, Math.ceil(this.total / this.size)); }
  get currentMember() { return this.items[0] ?? null; }
  get reportSections() {
    const card = this.currentMember?.summary;
    return [
      {field: 'finaltexts', heading: 'Final Diagnosis'},
      {field: 'commenttexts', heading: 'Diagnostic Comment'},
      {field: 'grosstexts', heading: 'Gross Description'},
      {field: 'synoptictexts', heading: 'Synoptic'},
      {field: 'intraoptexts', heading: 'Intraoperative Diagnosis'},
      {field: 'microscopictexts', heading: 'Microscopic Description'}
    ].map(section => ({heading: section.heading + ': ',
      content: Array.isArray(card?.[section.field])
        ? card[section.field].filter((text: unknown) => typeof text === 'string' && text.trim()) : []
    })).filter(section => section.content.length > 0);
  }
  trackReportSection(_: number, section: {heading: string}) { return section.heading; }
  get controlsDisabled() { return this.busy || this.pendingCaseId !== null || this.specimenLoading || this.specimenSaving; }
  get availableSpecimens() { return this.specimens.filter(specimen => specimen.available); }
  get selectedSpecimenCount() { return this.specimens.filter(specimen => specimen.selected).length; }
  get allSpecimensSelected() { return this.availableSpecimens.length > 0 && this.availableSpecimens.every(specimen => specimen.selected); }
  get someSpecimensSelected() { return !this.allSpecimensSelected && this.availableSpecimens.some(specimen => specimen.selected); }
  trackSpecimen(_: number, specimen: CaseSetSpecimen) { return specimen.specimenId; }

  async loadSpecimens(member = this.currentMember) {
    if (!member || this.specimenLoading || this.specimenSaving) return;
    this.specimenLoading = true; this.specimensLoaded = false;
    this.specimenError = ''; this.specimenSaved = ''; this.specimens = [];
    try {
      const result = await this.api.specimens(this.id, member.caseId);
      if (this.destroyed || this.currentMember !== member) return;
      this.specimens = result.specimens; this.specimensLoaded = true;
      Object.assign(member, result.member); this.set = result.set;
    } catch (error) { this.specimenError = caseSetError(error); }
    finally { this.specimenLoading = false; }
  }
  async toggleSpecimen(specimen: CaseSetSpecimen, event: Event) {
    const input = event.target as HTMLInputElement;
    const checked = input.checked;
    input.checked = specimen.selected;
    if (!specimen.available && checked) return;
    const ids = new Set(this.specimens.filter(item => item.selected).map(item => item.specimenId));
    if (checked) ids.add(specimen.specimenId); else ids.delete(specimen.specimenId);
    await this.saveSpecimens([...ids]);
  }
  async toggleAllSpecimens(event: Event) {
    const input = event.target as HTMLInputElement;
    const checked = input.checked;
    input.checked = this.allSpecimensSelected;
    input.indeterminate = this.someSpecimensSelected;
    await this.saveSpecimens(checked
      ? this.specimens.filter(item => item.available || item.selected).map(item => item.specimenId) : []);
  }
  async saveSpecimens(ids: number[]) {
    const member = this.currentMember;
    if (!member || this.controlsDisabled || !this.specimensLoaded) return;
    this.specimenSaving = true; this.specimenError = ''; this.specimenSaved = '';
    try {
      const result = await this.api.selectSpecimens(this.id, member, ids);
      if (this.destroyed || this.currentMember !== member) return;
      this.specimens = result.specimens; Object.assign(member, result.member); this.set = result.set;
      this.specimenSaved = 'Specimen selections saved.';
    } catch (error) {
      this.specimenError = 'Specimen selections could not be saved. ' + caseSetError(error);
    } finally { this.specimenSaving = false; }
  }

  async reload() {
    if (this.controlsDisabled || this.capturing) return;
    this.busy = true; this.error = '';
    try { this.set = await this.api.detail(this.id); }
    catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
    if (this.destroyed || !this.set) return;
    if (this.set.captureState === 'READY' && !this.set.archived) await this.load(true);
    else if (this.set.captureState === 'CAPTURING' && !this.set.archived) await this.capture();
  }
  async capture() {
    if (this.capturing || !this.set || this.set.archived) return;
    this.capturing = true; this.pauseRequested = false; this.error = '';
    try {
      while (!this.destroyed && !this.pauseRequested && this.set.captureState !== 'READY') {
        this.set = await this.api.capture(this.set);
        if (this.set.captureState === 'FAILED') { this.error = this.set.captureError; break; }
      }
    } catch (error) { this.error = caseSetError(error); }
    finally { this.capturing = false; }
    if (!this.destroyed && this.set.captureState === 'READY') await this.load(true);
  }
  async load(resume = false, page = this.page, filter = this.filter) {
    if (this.busy || this.destroyed || this.specimenLoading || this.specimenSaving) return;
    this.busy = true; this.error = '';
    try {
      const result = await this.api.members(this.id, filter, page, this.size, resume);
      if (this.destroyed) return;
      this.set = result.set; this.items = result.items; this.total = result.total;
      this.page = result.page; this.filter = result.filter;
      this.specimens = []; this.specimensLoaded = false; this.specimenError = ''; this.specimenSaved = '';
      if (this.caseContent) this.caseContent.nativeElement.scrollTop = 0;
      if (this.currentMember) await this.loadSpecimens(this.currentMember);
      if (!resume) await this.remember(this.items[0] ?? null);
    } catch (error) { this.error = caseSetError(error); }
    finally {
      this.busy = false; this.selectedFilter = this.filter;
      // Restore the displayed selection even when a request fails before change detection.
      this.filterControl?.control.setValue(this.filter, {emitEvent: false, emitViewToModelChange: false});
    }
  }
  async changeFilter(filter: ReviewFilter) {
    if (this.controlsDisabled) return;
    this.saved = ''; await this.load(false, 1, filter);
  }
  async go(page: number) {
    if (this.controlsDisabled || page < 1 || page > this.lastPage) return;
    this.saved = ''; await this.load(false, page);
  }
  async remember(member: CaseSetMember | null) {
    try { await this.api.position(this.id, member?.caseId ?? null, this.filter); }
    catch (error) { this.error = 'Your place could not be saved. ' + caseSetError(error); }
  }
  async decide(member: CaseSetMember, state: ReviewState) {
    if (this.controlsDisabled) return;
    this.pendingCaseId = member.caseId; this.error = ''; this.saved = '';
    try {
      const result = await this.api.decide(this.id, member, state);
      if (this.destroyed) return;
      Object.assign(member, result.member); this.set = result.set;
      this.saved = state === 'UNREVIEWED' ? `Case ${member.ordinal} reset to unreviewed.`
        : `Case ${member.ordinal}: ${state === 'INCLUDED' ? 'Included' : 'Excluded'}. Decision saved.`;
      if (this.filter !== 'ALL' && state !== this.filter) {
        // The reviewed case leaves this view, so its successor takes the same position.
        await this.load();
      } else if (state !== 'UNREVIEWED' && this.page < this.lastPage) {
        await this.load(false, this.page + 1);
      } else {
        await this.remember(member);
        if (state !== 'UNREVIEWED') this.saved += ' Last case in this view.';
      }
    } catch (error) { this.error = caseSetError(error); }
    finally { this.pendingCaseId = null; }
  }
}
