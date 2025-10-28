import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class RaceService {
  constructor(private http: HttpClient) { }

	getDataFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'race/active';
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

	async getAll(page: number, size: number) {
		const result: any = await this.getDataFromDB(page, size);
		return result;
	}

	insertIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'race/create';
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

	async create(data: any) {
		return await this.insertIntoDB(data);
	}

	getDetailFromDB(raceId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'race/get/'+raceId;
			
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

	async getDetail(raceId: number) {
		const result: any = await this.getDetailFromDB(raceId);
		return result;
	}

	updateIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'race/update';
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

	async update(data: any) {
		return await this.updateIntoDB(data);
	}

	deleteFromDB(raceId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'race/delete/'+raceId;
			
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

	async delete(raceId: number) {
		return await this.deleteFromDB(raceId);
	}
}
