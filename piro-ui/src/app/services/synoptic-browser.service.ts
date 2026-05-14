import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SynopticBrowserService {

  constructor(private http: HttpClient) {}

  private getProtocolsFromDB() {
    return new Promise((resolve, reject) => {
      const apiURL = environment.apiBaseUrl + environment.synopticBrowserUrl + '/protocols';
      this.http.get(apiURL).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: () => resolve({ status: false, data: [] }),
      });
    });
  }

  async getProtocols() {
    const result: any = await this.getProtocolsFromDB();
    return result;
  }

  private getTnmFacetsFromDB(protocol: string) {
    return new Promise((resolve, reject) => {
      const apiURL =
        environment.apiBaseUrl +
        environment.synopticBrowserUrl +
        '/tnmfacets?protocol=' +
        encodeURIComponent(protocol);
      this.http.get(apiURL).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: () => resolve({ status: false, data: [] }),
      });
    });
  }

  async getTnmFacets(protocol: string) {
    const result: any = await this.getTnmFacetsFromDB(protocol);
    return result;
  }
}
