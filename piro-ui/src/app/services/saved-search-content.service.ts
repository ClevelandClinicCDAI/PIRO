import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SavedSearchContentService {

  constructor(private http: HttpClient) { }

	getContentFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'search/active';
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

	async getContent(page: number, size: number) {
		const result: any = await this.getContentFromDB(page, size);
		return result;
	}
	getDropdownContentFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'search/dropdown';
			let query = {				 
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

	async getDropdown(page: number, size: number) {
		const result: any = await this.getDropdownContentFromDB();
		return result;
	}
	
	deleteContentFromDB(searchId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'search/delete/'+searchId;
			this.http.delete(apiURL)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true });
					},
					error: (err: any) => {
						resolve({ status: false, err: err });
					},
					complete: () => {

					},
				});
		});
		return promise;
	}
	async deletContent(searchId: number) {
		return await this.deleteContentFromDB(searchId);
	}
}
