import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RoleService {

  constructor(private http: HttpClient) { }

	getRolesFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/active';
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

	async getRoles(page: number, size: number) {
		const result: any = await this.getRolesFromDB(page, size);
		return result;
	}

	insertRoleIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/create';
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

	async createRole(data: any) {
		return await this.insertRoleIntoDB(data);
	}

	getRoleDetailFromDB(roleId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/get/'+roleId;
			
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

	async getRoleDetail(roleId: number) {
		const result: any = await this.getRoleDetailFromDB(roleId);
		return result;
	}

	updateRoleIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/update';
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

	async updateRole(data: any) {
		return await this.updateRoleIntoDB(data);
	}

	deleteRoleFromDB(roleId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/delete/'+roleId;
			
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

	async deleteRole(roleId: number) {
		return await this.deleteRoleFromDB(roleId);
	}


	getRolesDropdownFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'role/dropdown';
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

	async getRolesDropdown() {
		const result: any = await this.getRolesDropdownFromDB();
		return result;
	}

}
