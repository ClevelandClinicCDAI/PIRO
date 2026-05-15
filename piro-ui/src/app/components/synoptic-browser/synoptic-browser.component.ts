import { Component, ElementRef, ViewChild, OnDestroy } from '@angular/core';
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } from 'chart.js';
import { ToastrService } from 'ngx-toastr';
import { SynopticBrowserService } from '../../services/synoptic-browser.service';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

interface Protocol {
  protocol: string;
  case_count: number;
  checked: boolean;
}

interface TnmFacetItem {
  key: string;
  value: string;
  case_count: number;
  checked: boolean;
}

interface TnmGroup {
  label: string;
  items: TnmFacetItem[];
}

@Component({
  selector: 'app-synoptic-browser',
  templateUrl: './synoptic-browser.component.html',
  styleUrls: ['./synoptic-browser.component.css']
})
export class SynopticBrowserComponent implements OnDestroy {

  @ViewChild('yearChart') yearChartRef!: ElementRef<HTMLCanvasElement>;
  private yearChart: Chart | null = null;

  view: 'protocols' | 'facets' = 'protocols';
  selectedProtocol: string = '';

  protocols: Protocol[] = [];
  tnmGroups: TnmGroup[] = [];
  matchingCaseCount: number = 0;
  selectedProtocolTotalCases: number = 0;

  protocolsLoaded = false;
  facetsLoaded = false;
  facetsUpdating = false;

  // Save cohort state
  showSaveForm = false;
  cohortName = '';
  cohortDescription = '';
  saving = false;

  constructor(
    private synopticBrowserService: SynopticBrowserService,
    private toastr: ToastrService
  ) {}

  async ngOnInit() {
    await this.loadProtocols();
  }

  ngOnDestroy() {
    this.yearChart?.destroy();
  }

  async loadProtocols() {
    this.protocolsLoaded = false;
    const result = await this.synopticBrowserService.getProtocols();
    if (result.status) {
      this.protocols = result.data.map((p: any) => ({ ...p, checked: false }));
    }
    this.protocolsLoaded = true;
  }

  async onProtocolChange(protocol: Protocol) {
    this.protocols.forEach(p => p.checked = false);
    protocol.checked = true;
    this.selectedProtocol = protocol.protocol;
    this.selectedProtocolTotalCases = protocol.case_count;
    this.view = 'facets';
    this.facetsLoaded = false;
    this.tnmGroups = [];
    this.matchingCaseCount = 0;
    this.showSaveForm = false;

    const result = await this.synopticBrowserService.getFacets(protocol.protocol);
    if (result.status) {
      this.tnmGroups = this.buildFacetGroups(result.data.items, []);
      this.matchingCaseCount = result.data.total_cases;
    }
    this.facetsLoaded = true;
    // Defer chart render one tick so *ngIf renders the canvas first
    setTimeout(() => this.renderYearChart(result.status ? (result.data.year_dist || []) : []), 0);
  }

  async onFacetFilterChange(changedItem: TnmFacetItem) {
    changedItem.checked = !changedItem.checked;
    const activeFilters = this.getActiveFilters();
    this.facetsUpdating = true;

    try {
      const result = await this.synopticBrowserService.getFacets(
        this.selectedProtocol,
        activeFilters
      );
      if (result.status) {
        this.mergeFacetCounts(result.data.items);
        this.matchingCaseCount = result.data.total_cases;
        this.renderYearChart(result.data.year_dist || []);
      }
    } finally {
      this.facetsUpdating = false;
    }
  }

  backToProtocols() {
    this.view = 'protocols';
    this.selectedProtocol = '';
    this.selectedProtocolTotalCases = 0;
    this.tnmGroups = [];
    this.matchingCaseCount = 0;
    this.showSaveForm = false;
    this.protocols.forEach(p => p.checked = false);
  }

  getActiveFilters(): { key: string; value: string }[] {
    const filters: { key: string; value: string }[] = [];
    for (const group of this.tnmGroups) {
      for (const item of group.items) {
        if (item.checked) filters.push({ key: item.key, value: item.value });
      }
    }
    return filters;
  }

  clearAllFilters() {
    this.tnmGroups.forEach(g => g.items.forEach(i => i.checked = false));
    this.facetsUpdating = true;
    this.synopticBrowserService.getFacets(this.selectedProtocol).then(result => {
      if (result.status) {
        this.mergeFacetCounts(result.data.items);
        this.matchingCaseCount = result.data.total_cases;
        this.renderYearChart(result.data.year_dist || []);
      }
      this.facetsUpdating = false;
    });
  }

  toggleSaveForm() {
    this.showSaveForm = !this.showSaveForm;
    if (this.showSaveForm) {
      this.cohortName = this.selectedProtocol;
      this.cohortDescription = '';
    }
  }

  async saveCohort() {
    if (!this.cohortName.trim()) {
      this.toastr.warning('Please enter a cohort name.', '');
      return;
    }
    this.saving = true;
    const result = await this.synopticBrowserService.saveCohort(
      this.selectedProtocol,
      this.getActiveFilters(),
      this.cohortName.trim(),
      this.cohortDescription.trim()
    );
    this.saving = false;
    if (result.status) {
      this.toastr.success(`Cohort "${this.cohortName}" saved successfully.`, 'Cohort Created');
      this.showSaveForm = false;
      this.cohortName = '';
      this.cohortDescription = '';
    } else {
      this.toastr.error(result.message || 'Failed to save cohort.', 'Error');
    }
  }

  get hasActiveFilters(): boolean {
    return this.tnmGroups.some(g => g.items.some(i => i.checked));
  }

  private buildFacetGroups(
    items: { key: string; value: string; case_count: number }[],
    previousChecked: { key: string; value: string }[]
  ): TnmGroup[] {
    const checkedSet = new Set(previousChecked.map(f => `${f.key}||${f.value}`));
    const groupMap = new Map<string, TnmFacetItem[]>();
    for (const item of items) {
      const facetItem: TnmFacetItem = {
        ...item,
        checked: checkedSet.has(`${item.key}||${item.value}`)
      };
      const existing = groupMap.get(item.key) || [];
      existing.push(facetItem);
      groupMap.set(item.key, existing);
    }

    // TNM categories always appear first in this order, then all other keys alphabetically
    const tnmOrder = ['pT category', 'pN category', 'pM category'];
    const groups: TnmGroup[] = [];

    for (const prefix of tnmOrder) {
      for (const [key, groupItems] of groupMap.entries()) {
        if (key.toLowerCase().includes(prefix.toLowerCase()) && !groups.find(g => g.label === key)) {
          groups.push({ label: key, items: groupItems });
        }
      }
    }

    const tnmKeys = new Set(groups.map(g => g.label));
    const remainingKeys = [...groupMap.keys()]
      .filter(k => !tnmKeys.has(k))
      .sort((a, b) => a.localeCompare(b));

    for (const key of remainingKeys) {
      groups.push({ label: key, items: groupMap.get(key)! });
    }

    return groups;
  }

  private mergeFacetCounts(updatedItems: { key: string; value: string; case_count: number }[]) {
    const countMap = new Map<string, number>();
    for (const item of updatedItems) {
      countMap.set(`${item.key}||${item.value}`, item.case_count);
    }
    for (const group of this.tnmGroups) {
      for (const item of group.items) {
        const newCount = countMap.get(`${item.key}||${item.value}`);
        item.case_count = newCount !== undefined ? newCount : 0;
      }
    }
  }

  private renderYearChart(yearDist: { year: number; case_count: number }[]) {
    const canvas = this.yearChartRef?.nativeElement;
    if (!canvas) return;

    this.yearChart?.destroy();
    this.yearChart = null;

    if (!yearDist.length) return;

    this.yearChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: yearDist.map(d => String(d.year)),
        datasets: [{
          data: yearDist.map(d => d.case_count),
          backgroundColor: '#0078bf',
          borderRadius: 3,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { mode: 'index' } },
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }

  trackByProtocol(_: number, p: Protocol) { return p.protocol; }
  trackByGroup(_: number, g: TnmGroup) { return g.label; }
  trackByItem(_: number, i: TnmFacetItem) { return i.key + '|' + i.value; }
}
