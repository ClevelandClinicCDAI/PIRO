import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SpecimenTypeService {
  constructor(private http: HttpClient) { }

	getSpecimenTypesFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimentype/active';
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

	async getSpecimenTypes(page: number, size: number) {
		const result: any = await this.getSpecimenTypesFromDB(page, size);
		return result;
	}

	insertSpecimenTypeIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimentype/create';
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

	async createSpecimenType(data: any) {
		return await this.insertSpecimenTypeIntoDB(data);
	}

	getSpecimenTypeDetailFromDB(specimenTypeId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimentype/get/'+specimenTypeId;
			
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

	async getSpecimenTypeDetail(specimenTypeId: number) {
		const result: any = await this.getSpecimenTypeDetailFromDB(specimenTypeId);
		return result;
	}

	updateSpecimenTypeIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimentype/update';
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

	async updateSpecimenType(data: any) {
		return await this.updateSpecimenTypeIntoDB(data);
	}

	deleteSpecimenTypeFromDB(specimenTypeId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'specimentype/delete/'+specimenTypeId;
			
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

	async deleteSpecimenType(specimenTypeId: number) {
		return await this.deleteSpecimenTypeFromDB(specimenTypeId);
	}
}
