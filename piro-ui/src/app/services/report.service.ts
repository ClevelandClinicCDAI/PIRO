import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
	providedIn: 'root'
})
export class ReportService {
	constructor(private http: HttpClient) { }

	getAuditTrailFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'report/audittrailsearch';
			let query = {
				params: {}
			}
			this.http.get<any>(apiURL, query)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: [] })
					},
					complete: () => {

					},
				});
		});
		return promise;
	}

	async getAuditTrailReport() {
		const result: any = await this.getAuditTrailFromDB();
		return result;
	}
}
