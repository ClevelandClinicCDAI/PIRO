import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest, Subscription } from 'rxjs';
import { CaseSetService, TeachingCase, TeachingSetSummary, caseSetError } from '../../services/case-set.service';

@Component({standalone: false, selector: 'app-teaching-set-view',
  templateUrl: './teaching-set-view.component.html', styleUrls: ['./case-sets.css']})
export class TeachingSetViewComponent implements OnInit, OnDestroy {
  id = 0; page = 1; total = 0; busy = false; error = '';
  set: TeachingSetSummary | null = null; member: TeachingCase | null = null;
  reportSections: {heading: string; content: string[]}[] = [];
  specialty = ''; browsePage = 1;
  private request = 0;
  private subscription?: Subscription;
  @ViewChild('caseContent') private caseContent?: ElementRef<HTMLElement>;
  constructor(private api: CaseSetService, private route: ActivatedRoute, private router: Router) {}
  ngOnInit() {
    this.subscription = combineLatest([this.route.paramMap, this.route.queryParamMap]).subscribe(([params, query]) => {
      this.id = Number(params.get('id'));
      this.page = Math.max(1, Number(query.get('page')) || 1);
      this.specialty = query.get('specialty') || ''; this.browsePage = Math.max(1, Number(query.get('browsePage')) || 1);
      void this.load();
    });
  }
  ngOnDestroy() { this.subscription?.unsubscribe(); this.request++; }
  private buildReportSections(card: TeachingCase['summary']) {
    return [
      {field: 'finaltexts', heading: 'Final Diagnosis'},
      {field: 'commenttexts', heading: 'Diagnostic Comment'},
      {field: 'grosstexts', heading: 'Gross Description'},
      {field: 'synoptictexts', heading: 'Synoptic'},
      {field: 'intraoptexts', heading: 'Intraoperative Diagnosis'},
      {field: 'microscopictexts', heading: 'Microscopic Description'}
    ].map(section => ({heading: section.heading + ': ', content: Array.isArray(card?.[section.field])
      ? card[section.field].filter((value: unknown) => typeof value === 'string' && value.trim()) : []}))
      .filter(section => section.content.length > 0);
  }
  async load() {
    const request = ++this.request;
    this.busy = true; this.error = ''; this.set = null; this.member = null;
    this.reportSections = [];
    try {
      const result = await this.api.teachingCases(this.id, this.page);
      if (request !== this.request) return;
      this.set = result.set; this.member = result.items[0] || null;
      // Keep section identities stable while asynchronous report formatting
      // triggers change detection; rebuilding them there causes a render loop.
      this.reportSections = this.buildReportSections(this.member?.summary);
      this.total = result.total; this.page = result.page;
      if (this.caseContent) this.caseContent.nativeElement.scrollTop = 0;
    } catch (error) { if (request === this.request) this.error = caseSetError(error); }
    finally { if (request === this.request) this.busy = false; }
  }
  go(page: number) {
    if (this.busy || page < 1 || page > this.total) return;
    return this.router.navigate([], {relativeTo: this.route, queryParams: {page}, queryParamsHandling: 'merge'});
  }
}
