import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SpecimenSourceService {
  constructor(private http: HttpClient) { }

	getSpecimenSourcesFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimensource/active';
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

	async getSpecimenSources(page: number, size: number) {
		const result: any = await this.getSpecimenSourcesFromDB(page, size);
		return result;
	}

	insertSpecimenSourceIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimensource/create';
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

	async createSpecimenSource(data: any) {
		return await this.insertSpecimenSourceIntoDB(data);
	}

	getSpecimenSourceDetailFromDB(specimenSourceId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimensource/get/'+specimenSourceId;
			
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

	async getSpecimenSourceDetail(specimenSourceId: number) {
		const result: any = await this.getSpecimenSourceDetailFromDB(specimenSourceId);
		return result;
	}

	updateSpecimenSourceIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimensource/update';
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

	async updateSpecimenSource(data: any) {
		return await this.updateSpecimenSourceIntoDB(data);
	}

	deleteSpecimenSourceFromDB(specimenSourceId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimensource/delete/'+specimenSourceId;
			
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

	async deleteSpecimenSource(specimenSourceId: number) {
		return await this.deleteSpecimenSourceFromDB(specimenSourceId);
	}
}
