import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
	providedIn: 'root'
})
export class ExtractRequestService {

	constructor(private http: HttpClient) { }

	getDropdownReasonsFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/reasondropdown';
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

	insertRequestIntoDBFile(data: any, isFile: boolean) {
		const options = {} as any;
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequest/createrequest';
			if(!isFile) {
				apiURL = environment.apiBaseUrl + 'searchrequest/createrequestlite';
			}
			this.http.post(apiURL, data, { headers: new HttpHeaders({ 'ContentType': 'false' }) })
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

	async createRequest(data: any, isFile: boolean) {
		return await this.insertRequestIntoDBFile(data, isFile);
	}


	getDataFields() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequestfield/getdatafields';
			let query = {
			}
			this.http.get<any>(apiURL, query)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: {"categories": [], "fields": []} })
					},
					complete: () => {

					},
				});
		});
		return promise;
	}

	getDataFieldsForRequest(searchRequestId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequestfield/get/' + searchRequestId;
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

	saveDataFieldsForRequest(searchRequestId: number, fieldIds: [number]) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'searchrequestfield/update';			 
			this.http.post(apiURL,{"searchrequestId": searchRequestId, "dataFields": fieldIds}).subscribe({
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
}
