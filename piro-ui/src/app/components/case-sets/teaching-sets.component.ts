import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { CaseSetService, TeachingSetSummary, caseSetError } from '../../services/case-set.service';

@Component({standalone: false, selector: 'app-teaching-sets',
  templateUrl: './teaching-sets.component.html', styleUrls: ['./case-sets.css']})
export class TeachingSetsComponent implements OnInit, OnDestroy {
  items: TeachingSetSummary[] = []; categories: string[] = [];
  specialty = ''; page = 1; size = 25; total = 0; busy = false; error = '';
  private request = 0;
  private subscription?: Subscription;
  constructor(private api: CaseSetService, private route: ActivatedRoute, private router: Router) {}
  ngOnInit() {
    this.subscription = this.route.queryParamMap.subscribe(params => {
      this.specialty = params.get('specialty') || '';
      this.page = Math.max(1, Number(params.get('page')) || 1);
      void this.load();
    });
  }
  ngOnDestroy() { this.subscription?.unsubscribe(); this.request++; }
  async load() {
    const request = ++this.request;
    this.busy = true; this.error = ''; this.items = []; this.total = 0;
    try {
      const result = await this.api.teachingSets(this.specialty, this.page);
      if (request !== this.request) return;
      this.items = result.items; this.total = result.total; this.page = result.page;
      this.size = result.size; this.categories = result.categories;
    } catch (error) { if (request === this.request) this.error = caseSetError(error); }
    finally { if (request === this.request) this.busy = false; }
  }
  browse(page = 1) {
    return this.router.navigate([], {relativeTo: this.route,
      queryParams: {specialty: this.specialty || null, page}, queryParamsHandling: 'merge'});
  }
}
