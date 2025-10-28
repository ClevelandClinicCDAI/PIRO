import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CohortService {

  constructor(private http: HttpClient) { }

  insertIntoDB(data: any, isFile: boolean) {
		const options = {} as any;
		let promise = new Promise((resolve, reject) => {
			let apiURL = '';
			if(isFile) {
				apiURL = environment.apiBaseUrl + 'cohort/create';
			} else {
				apiURL = environment.apiBaseUrl + 'cohort/update';
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
		return await this.insertIntoDB(data, isFile);
	}

	getDataFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'cohort/all';
			let query = {
				params: {

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

	async getAll() {
		const result: any = await this.getDataFromDB();
		return result;
	}


	async getCohortFacet() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'cohort/facetlist';
			let query = {
				params: {

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

		const result: any = await promise;
		return result;
	}


	async export(id: number) {
		const apiURL = environment.apiBaseUrl + 'cohort/export/'+id;
		return this.http.get(apiURL, {
			observe: 'response',
			responseType: 'blob',
			headers:
				{ 'Access-Control-Allow-Origin': '*' }
		});
	}

	async exportMRNTemplate() {
		const apiURL = environment.apiBaseUrl + 'cohort/template/mrn';
		return this.http.get(apiURL, {
			observe: 'response',
			responseType: 'blob',
			headers:
				{ 'Access-Control-Allow-Origin': '*',
					'Cache-Control':'no-cache'
				 }
		});
	}

	async exportCaseTemplate() {
		const apiURL = environment.apiBaseUrl + 'cohort/template/case';
		return this.http.get(apiURL, {
			observe: 'response',
			responseType: 'blob',
			headers:
				{ 'Access-Control-Allow-Origin': '*',
					'Cache-Control':'no-cache'
				 }
		});
	}

	async exportEIDTemplate() {
		const apiURL = environment.apiBaseUrl + 'cohort/template/eid';
		return this.http.get(apiURL, {
			observe: 'response',
			responseType: 'blob',
			headers:
				{ 'Access-Control-Allow-Origin': '*',
					'Cache-Control':'no-cache'
				 }
		});
	}

	getDataByIdFromDB(id: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'cohort/get/'+id;
			let query = {
				params: {

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

	async getDataById(id: number) {
		const result: any = await this.getDataByIdFromDB(id);
		return result;
	}

	deleteFromDB(id: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'cohort/delete/'+id;
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
	async delete(id: number) {
		return await this.deleteFromDB(id);
	}

	private getStatus = new BehaviorSubject<any>({
		status: false
	});
	private getStatus$ = this.getStatus.asObservable();

	getStatusCount(): Observable<any> {
		return this.getStatus$;
	}

	setStatusCount(latestValue: boolean) {
		return this.getStatus.next({ status: latestValue });
	}
}
