import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RequesthistoryService {
	
  constructor(private http: HttpClient) { }

	getAllFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/allsubmit';
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

	getMyFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/mysubmit';
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

	getAllStatusFromDB(status: string, page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/getall/' + status;
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

	deleteFromDB(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/delete/' + searchRequestId;
			 
			this.http.delete<any>(apiURL)
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

	getExcelFromDB(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/export/' + searchRequestId;
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


	async getAll(page: number, size: number) {
		const result: any = await this.getAllFromDB(page, size);
		return result;
	}

	async getMy(page: number, size: number) {
		const result: any = await this.getMyFromDB(page, size);
		return result;
	}

	async getAllStatus(status: string, page: number, size: number) {
		const result: any = await this.getAllStatusFromDB(status, page, size);
		return result;
	}	

	async delete(searchRequestId: number) {
		const result: any = await this.deleteFromDB(searchRequestId);
		return result;
	}

	async approve(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/approve/' + searchRequestId;
			 
			this.http.post<any>(apiURL, {})
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
		const result: any = await promise;
		return result;
	}


	async deny(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/deny/' + searchRequestId;
			 
			this.http.post<any>(apiURL, {})
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
		const result: any = await promise;
		return result;
	}

	async close(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/close/' + searchRequestId;
			 
			this.http.post<any>(apiURL, {})
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
		const result: any = await promise;
		return result;
	}

	async startExtraction(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/startextraction/' + searchRequestId;

			this.http.post<any>(apiURL, {})
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: [], err: err.error?.detail || err.message })
					},
					complete: () => {

					},
				});
		});
		const result: any = await promise;
		return result;
	}

	getExport(searchRequestId: number) {
		let apiURL = environment.apiBaseUrl + 'searchrequest/export/' + searchRequestId;
		return this.http.get(apiURL, {
			reportProgress: true,
			observe: 'events', 	
			responseType: 'blob'
		});
	}

	getFile(searchRequestId: number) {
		let apiURL = environment.apiBaseUrl + 'searchrequest/download/' + searchRequestId;
		return this.http.get(apiURL, {
			// reportProgress: true,
			observe: 'response', 	
			responseType: 'blob',
			headers: 
				{'Access-Control-Allow-Origin': '*' }
		});
	}


	async getRequest(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/get/' + searchRequestId;
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

	async updateComment(searchRequestId: number, comment: string) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/approvalcomment/';
			 
			this.http.post<any>(apiURL, {"searchRequestId": searchRequestId, "approvalComment": comment})
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
		const result: any = await promise;
		return result;
	}
}
