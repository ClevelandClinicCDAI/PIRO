import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
	providedIn: 'root'
})
export class UserService {

	constructor(private http: HttpClient) { }

	getUsersFromDB(page:number,size:number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/active';
			let query = {
				params: {
					page: page,
					size: size
				}
			}
			this.http.get(apiURL, query)
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

	async getUsers(page:number,size:number) {
		const result: any = await this.getUsersFromDB(page,size);
		return result;
	}

	insertUserIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/create';
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

	async createUser(data: any) {
		return await this.insertUserIntoDB(data);
	}

	getUserDetailFromDB(userId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/get/'+userId;
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

	async getUserDetail(userId: number) {
		const result: any = await this.getUserDetailFromDB(userId);
		return result;
	}

	updateUserIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/update';
			this.http.post(apiURL, data)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {						
						resolve({ status: false, data: [], err: err })
					},
					complete: () => {

					},
				});
		});
		return promise;
	}

	async updateUser(data: any) {
		return await this.updateUserIntoDB(data);
	}

	deleteUserFromDB(userId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/delete/'+ userId;
			// let query = {
			// 	params: {
			// 		userId: userId
			// 	}
			// }
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
	async deletUser(userId: number) {
		return await this.deleteUserFromDB(userId);
	}

	updatePreferenceIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'user/update';
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

	async updatePreference(data: any) {
		return await this.updatePreferenceIntoDB(data);
	}
}
