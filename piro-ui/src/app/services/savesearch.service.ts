import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SavesearchService {

  constructor(private http: HttpClient) { }

  saveSearchIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'search/create';
			this.http.post(apiURL, data)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: [], err: err.message })
					},
					complete: () => {

					},
				});
		});
		return promise;
	}


	getSearchFromDB(serachId: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'search/display/' + serachId;
			this.http.get(apiURL)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: {}, err: err.message })
					},
					complete: () => {

					},
				});
		});
		return promise;
	}

	async saveSearch(data: any, advfields: any, mrn: any) {
		data.advfields = JSON.stringify(advfields);
		data.mrn = mrn;
		return await this.saveSearchIntoDB(data);
	}

	async getSearch(searchId: any) {
		return await this.getSearchFromDB(searchId);
	}

}
