import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpBackend, HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

interface Physician {
  physician_id: string; name: string; username: string; subspecialty: string; region: string;
  status: string; site: string; last_observed: string | null; events: any[];
  subspecialty_source?: string; recent_case_count?: number; classified_case_count?: number;
  role_evidence_cases?: number;
  case_mix?: {subspecialty: string; cases: number}[];
}
interface RosterMetadata {
  real_names: boolean; sample_cases?: number; earliest_accession?: string; latest_accession?: string; candidate_staff_count?: number;
}
@Component({
  standalone: true, selector: 'app-physician-location', imports: [CommonModule, FormsModule],
  templateUrl: './physician-location.component.html', styleUrls: ['./physician-location.component.css']
})
export class PhysicianLocationComponent implements OnInit, OnDestroy {
  physicians: Physician[] = []; query = ''; specialties = new Set<string>(); regions = new Set<string>();
  roster: RosterMetadata = {real_names: false};
  status = ''; day = new Intl.DateTimeFormat('en-CA', {timeZone:'America/New_York'}).format(new Date());
  page = 1; pageSize = 25; sortKey: keyof Physician = 'name'; ascending = true;
  expanded = ''; error = ''; loading = false; updated = ''; notice = ''; timer?: ReturnType<typeof setInterval>;
  private http: HttpClient;
  constructor(backend: HttpBackend) { this.http = new HttpClient(backend); }
  ngOnInit() { this.refresh(); this.timer = setInterval(() => this.refresh(), 5000); }
  ngOnDestroy() { if (this.timer) clearInterval(this.timer); }
  async refresh() {
    if (this.loading) return;
    this.loading = true;
    const requestedDay = this.day;
    try {
      const data: any = await firstValueFrom(this.http.get('/api/work-location/physicians', {params:{day:requestedDay}}));
      if (requestedDay === this.day) { this.physicians = data.physicians; this.roster = data.roster || {real_names: false}; this.error = ''; this.updated = new Date().toLocaleTimeString(); }
    } catch { this.error = 'Location service unavailable. Displayed observations may be out of date. Start the local prototype services and retry.'; }
    finally { this.loading = false; }
  }
  changeDay() { this.page = 1; this.expanded = ''; this.physicians = []; this.refresh(); }
  get specialtyOptions() { return [...new Set(this.physicians.map(p=>p.subspecialty))].sort(); }
  get regionOptions() { return [...new Set(this.physicians.map(p=>p.region))].sort(); }
  count(field: 'subspecialty'|'region', value:string) { return this.physicians.filter(p=>p[field]===value).length; }
  toggle(set:Set<string>, value:string) { set.has(value) ? set.delete(value) : set.add(value); this.page = 1; }
  clear() { this.query=''; this.specialties.clear(); this.regions.clear(); this.status=''; this.page=1; }
  get filtered() {
    const q=this.query.toLowerCase().trim();
    return this.physicians.filter(p => (!q || [p.name,p.username,p.subspecialty,p.region,p.site].join(' ').toLowerCase().includes(q))
      && (!this.specialties.size || this.specialties.has(p.subspecialty)) && (!this.regions.size || this.regions.has(p.region))
      && (!this.status || p.status===this.status)).sort((a,b)=>String(a[this.sortKey]??'').localeCompare(String(b[this.sortKey]??''))*(this.ascending?1:-1));
  }
  get pages() { return Math.max(1,Math.ceil(this.filtered.length/this.pageSize)); }
  get currentPage() { return Math.min(this.page,this.pages); }
  get visible() { return this.filtered.slice((this.currentPage-1)*this.pageSize,this.currentPage*this.pageSize); }
  get first() { return this.filtered.length ? (this.currentPage-1)*this.pageSize+1 : 0; }
  get last() { return Math.min(this.currentPage*this.pageSize,this.filtered.length); }
  sort(key:keyof Physician) { this.ascending=this.sortKey===key?!this.ascending:true; this.sortKey=key; }
  badge(status:string) { return status==='In Office'?'office':status==='Remote'?'remote':status==='Unknown'?'unknown':'inactive'; }
  time(value:string|null) { return value ? new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',hour:'numeric',minute:'2-digit',second:'2-digit'}).format(new Date(value)) : '—'; }
  save() {
    try { localStorage.setItem('piro-presence-filters',JSON.stringify({query:this.query,specialties:[...this.specialties],regions:[...this.regions],status:this.status})); this.notice='Filters saved in this browser.'; }
    catch { this.notice='Unable to save filters in this browser.'; }
  }
  load() {
    try { const raw=localStorage.getItem('piro-presence-filters'); if (!raw) {this.notice='No saved filters yet.'; return;}
      const x=JSON.parse(raw); this.query=typeof x.query==='string'?x.query:''; this.specialties=new Set(Array.isArray(x.specialties)?x.specialties:[]); this.regions=new Set(Array.isArray(x.regions)?x.regions:[]); this.status=x.status||''; this.page=1; this.notice='Saved filters loaded.';
    } catch { this.notice='Saved filters could not be loaded.'; }
  }
}
