import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SynopticBrowserService {

  constructor(private http: HttpClient) {}

  private getProtocolsFromDB() {
    return new Promise((resolve) => {
      const apiURL = environment.apiBaseUrl + environment.synopticBrowserUrl + '/protocols';
      this.http.get(apiURL).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: () => resolve({ status: false, data: [] }),
      });
    });
  }

  async getProtocols() {
    return await this.getProtocolsFromDB() as any;
  }

  private getTnmFacetsFromDB(protocol: string, filters: { key: string; value: string }[]) {
    return new Promise((resolve) => {
      const apiURL = environment.apiBaseUrl + environment.synopticBrowserUrl + '/tnmfacets';
      this.http.post(apiURL, { protocol, filters }).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: () => resolve({ status: false, data: { items: [], total_cases: 0 } }),
      });
    });
  }

  async getTnmFacets(protocol: string, filters: { key: string; value: string }[] = []) {
    return await this.getTnmFacetsFromDB(protocol, filters) as any;
  }

  private saveCohortToDB(
    protocol: string,
    filters: { key: string; value: string }[],
    name: string,
    description: string
  ) {
    return new Promise((resolve) => {
      const apiURL = environment.apiBaseUrl + environment.synopticBrowserUrl + '/savecohort';
      this.http.post(apiURL, { protocol, filters, name, description }).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, message: err?.error?.detail || 'Error saving cohort' }),
      });
    });
  }

  async saveCohort(
    protocol: string,
    filters: { key: string; value: string }[],
    name: string,
    description: string
  ) {
    return await this.saveCohortToDB(protocol, filters, name, description) as any;
  }
}
