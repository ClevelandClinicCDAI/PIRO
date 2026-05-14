import { Component } from '@angular/core';
import { SynopticBrowserService } from '../../services/synoptic-browser.service';

interface Protocol {
  protocol: string;
  case_count: number;
}

interface TnmFacetItem {
  key: string;
  value: string;
  case_count: number;
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

  protocolsLoaded = false;
  facetsLoaded = false;

  constructor(private synopticBrowserService: SynopticBrowserService) {}

  async ngOnInit() {
    await this.loadProtocols();
  }

  async loadProtocols() {
    this.protocolsLoaded = false;
    const result = await this.synopticBrowserService.getProtocols();
    if (result.status) {
      this.protocols = result.data;
    }
    this.protocolsLoaded = true;
  }

  async selectProtocol(protocol: string) {
    this.selectedProtocol = protocol;
    this.view = 'facets';
    this.facetsLoaded = false;
    this.tnmGroups = [];

    const result = await this.synopticBrowserService.getTnmFacets(protocol);
    if (result.status) {
      this.tnmGroups = this.buildTnmGroups(result.data);
    }
    this.facetsLoaded = true;
  }

  backToProtocols() {
    this.view = 'protocols';
    this.selectedProtocol = '';
    this.tnmGroups = [];
  }

  private buildTnmGroups(items: TnmFacetItem[]): TnmGroup[] {
    const groupMap = new Map<string, TnmFacetItem[]>();
    for (const item of items) {
      const existing = groupMap.get(item.key) || [];
      existing.push(item);
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
    // Append any remaining keys not matched by the preferred order
    for (const [key, groupItems] of groupMap.entries()) {
      if (!groups.find(g => g.label === key)) {
        groups.push({ label: key, items: groupItems });
      }
    }
    return groups;
  }

  trackByProtocol(_: number, p: Protocol) {
    return p.protocol;
  }

  trackByGroup(_: number, g: TnmGroup) {
    return g.label;
  }

  trackByItem(_: number, i: TnmFacetItem) {
    return i.key + '|' + i.value;
  }
}
