import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SaveTagService {

  
  constructor(private http: HttpClient) { }

  saveTagIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tag/create';
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

	async saveTag(data: any) {
		return await this.saveTagIntoDB(data);
	}

	getContentFromDB(page: number, size: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tag/all';
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

	deleteTagFromDB(id: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tag/delete/'+id;
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
	async deleteTag(id: number) {
		return await this.deleteTagFromDB(id);
	}

	getTagDropdownFromDB() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tag/dropdown';
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

	async getTagDropdown() {
		const result: any = await this.getTagDropdownFromDB();
		return result;
	}

	getCaseContentFromDB(caseid:number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tagcase/all/'+caseid;
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

	async getCaseTagContent(caseid:number) {
		const result: any = await this.getCaseContentFromDB(caseid);
		return result;
	}

	deleteCaseTagFromDB(id: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tagcase/delete/'+id;
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
	async deleteCaseTag(id: number) {
		return await this.deleteCaseTagFromDB(id);
	}

	saveCaseTagIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'tagcase/create';
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

	async saveCaseTag(data: any) {
		return await this.saveCaseTagIntoDB(data);
	}

	private getStatus = new BehaviorSubject<any>({
		status:false
	});
	private getStatus$ = this.getStatus.asObservable();

	getStatusCount(): Observable<any>{
		return this.getStatus$;
	}

	setStatusCount(latestValue:boolean){
		return this.getStatus.next({status:latestValue});
	}
}
