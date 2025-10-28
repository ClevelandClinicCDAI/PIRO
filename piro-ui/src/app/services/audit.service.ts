import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class AuditService {
  constructor(private http: HttpClient) { }

	getHistoryLatestFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'profile/historylatest';			 
			this.http.get<any>(apiURL)
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

	async getHistoryLatest() {
		const result: any = await this.getHistoryLatestFromDB();
		return result;
	}

	getHistoryAllFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'profile/historyall';
			let query = {
				params: {
					page: page,
					size: size
				}
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

	async getHistoryAll(page: number, size: number) {
		const result: any = await this.getHistoryAllFromDB(page, size);
		return result;
	}
}
