import { Component } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { SynopticBrowserService } from '../../services/synoptic-browser.service';

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
export class SynopticBrowserComponent {

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

    const result = await this.synopticBrowserService.getTnmFacets(protocol.protocol);
    if (result.status) {
      this.tnmGroups = this.buildTnmGroups(result.data.items, []);
      this.matchingCaseCount = result.data.total_cases;
    }
    this.facetsLoaded = true;
  }

  async onFacetFilterChange(changedItem: TnmFacetItem) {
    changedItem.checked = !changedItem.checked;
    const activeFilters = this.getActiveFilters();
    this.facetsUpdating = true;

    const result = await this.synopticBrowserService.getTnmFacets(
      this.selectedProtocol,
      activeFilters
    );
    if (result.status) {
      this.mergeFacetCounts(result.data.items);
      this.matchingCaseCount = result.data.total_cases;
    }
    this.facetsUpdating = false;
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
    this.synopticBrowserService.getTnmFacets(this.selectedProtocol).then(result => {
      if (result.status) {
        this.mergeFacetCounts(result.data.items);
        this.matchingCaseCount = result.data.total_cases;
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

  private buildTnmGroups(
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
    const order = ['pT category', 'pN category', 'pM category'];
    const groups: TnmGroup[] = [];
    for (const label of order) {
      for (const [key, groupItems] of groupMap.entries()) {
        if (key.toLowerCase().includes(label.toLowerCase()) && !groups.find(g => g.label === key)) {
          groups.push({ label: key, items: groupItems });
        }
      }
    }
    for (const [key, groupItems] of groupMap.entries()) {
      if (!groups.find(g => g.label === key)) {
        groups.push({ label: key, items: groupItems });
      }
    }
    return groups;
  }

  private mergeFacetCounts(updatedItems: { key: string; value: string; case_count: number }[]) {
    const countMap = new Map<string, number>();
    for (const item of updatedItems) {
      countMap.set(`${item.key}||${item.value}`, item.case_count);
    }
    for (const group of this.tnmGroups) {
      const groupHasChecked = group.items.some(i => i.checked);
      for (const item of group.items) {
        if (groupHasChecked && !item.checked) {
          // Within a group, checked options are mutually exclusive — zero out the rest
          item.case_count = 0;
        } else {
          const newCount = countMap.get(`${item.key}||${item.value}`);
          item.case_count = newCount !== undefined ? newCount : 0;
        }
      }
    }
  }

  trackByProtocol(_: number, p: Protocol) { return p.protocol; }
  trackByGroup(_: number, g: TnmGroup) { return g.label; }
  trackByItem(_: number, i: TnmFacetItem) { return i.key + '|' + i.value; }
}
