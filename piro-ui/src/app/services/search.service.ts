import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
	providedIn: 'root'
})
export class SearchService {


	constructor(private http: HttpClient) { }

	getAllFromDB(page: number, size: number, filter: any, advfilter: any, mrn: any, sortBy: any) {
		let promise : any = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.searchUrl;

			var searchUrl = window.location.pathname + window.location.search;
			if (!searchUrl.match('search')) {				 
				resolve({ status: false, data: [] });
			}

			let query = {
				"fields": filter,
				"advfields": JSON.stringify(advfilter),
				"mrn": mrn,
				url: searchUrl,
				page: page,
				sortby: sortBy,
				sortorder: 'desc',
			}
			this.http.post(apiURL, query)
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

	async getAll(page: number, size: number, filter: any, advfilter: any, mrn: any, sortBy: any) {
		const result: any = await this.getAllFromDB(page, size, filter, advfilter, mrn, sortBy);
		return result;
	}


	getTagsFromDB(caseId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.tagUrl + '/' + caseId;
			let query = {

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

	async getTags(caseId: number) {
		const result: any = await this.getTagsFromDB(caseId);
		return result;
	}

	getAllFacetsFromDB(filter: any, advfilter: any, mrn: any, cohortIds: []) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.facetUrl;

			let query = {
				"fields": filter,
				"advfields": JSON.stringify(advfilter),
				"mrn": mrn,
				url: '',
				page: 1,
				sortby: 'ancesion_date',
				sortorder: 'desc',
				"cohortIds": cohortIds
			}
			this.http.post(apiURL, query)
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

	async getAllFacets(filter: any, advfilter: any, mrn: any, cohortIds: []) {
		const result: any = await this.getAllFacetsFromDB(filter, advfilter, mrn, cohortIds);
		return result;
	}

	getAllFilterFromDB() {
		let promise = new Promise((resolve, reject) => {
			// let apiURL = environment.apiBaseUrl + 'solr/filterdata';
			let apiURL = environment.apiBaseUrl + environment.filterDataUrl;
			
			let query = {

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

	async getAllFilter() {
		const result: any = await this.getAllFilterFromDB();
		return result;
	}

	async getAdvancedFilter() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'solr/filteradvanceddata';
			let query = {

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
		return await promise;
	}

	async validateAdvancedFilter(advfilter: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'solr/validateadvsearch';

			let query = {				 
				"advfields": JSON.stringify(advfilter)
			}
			this.http.post(apiURL, query)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: err.message })
					},
					complete: () => {

					},
				});
		});		 
		return await promise;
	}


	getAutoSuggestDataFromDB(keyword: any, type: string) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = '';
			if (type == 'staffname') {
				apiURL = environment.apiBaseUrl + environment.suggestStaffUrl + '?input_val=' + keyword;
			} else if (type == 'casenumber') {
				apiURL = environment.apiBaseUrl + environment.suggestCaseUrl + '?input_val=' + keyword.toUpperCase();
			} else {
				apiURL = environment.apiBaseUrl + environment.suggestCommentUrl + '?input_val=' + keyword;
			}
			let query = {

			}
			this.http.post(apiURL, query)
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

	async getAutoSuggestData(keyword: any, type: string) {
		const result: any = await this.getAutoSuggestDataFromDB(keyword, type);
		return result;
	}

	private getStatus = new BehaviorSubject<any>({
		status: false,
		value: ''
	});
	private getStatus$ = this.getStatus.asObservable();


	getStatusCount(): Observable<any> {
		return this.getStatus$;
	}

	setStatusCount(latestValue: boolean, value: string) {
		return this.getStatus.next({ status: latestValue, value: value });
	}

	getCaseDetailFromDB(caseid: string) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.caseinfo;

			let query = {
				caseid: caseid
			}
			this.http.post(apiURL, query)
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

	async getCaseDetail(caseid: string) {
		const result: any = await this.getCaseDetailFromDB(caseid);
		return result;
	}

	getTextCommentsFromDB(caseId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.textCommentsUrl + '/' + caseId;
			let query = {

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

	async getTextComments(caseId: number) {
		const result: any = await this.getTextCommentsFromDB(caseId);
		return result;
	}

	getEpicCommentsFromDB(caseId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.epicCommentsUrl + '/' + caseId;
			let query = {

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

	async getEpicComments(caseId: number) {
		const result: any = await this.getEpicCommentsFromDB(caseId);
		return result;
	}

	getCoPathCommentsFromDB(caseId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.coPathCommentsUrl + '/' + caseId;
			let query = {

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

	async getCoPathComments(caseId: number) {
		const result: any = await this.getCoPathCommentsFromDB(caseId);
		return result;
	}

	async getSynopticComments(synopticId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.synopticCommentsUrl + '/' + synopticId;
			let query = {
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

		const result: any = await promise;
		return result;
	}


	async getAnnotationConfig() {
		let promise = new Promise((resolve, reject) => {			 
			let apiURL = environment.apiBaseUrl + environment.annotationConfigUrl;
			let query = {
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
		const result: any = await promise;
		return result;
	}

	async getFeedbackData(caseId: number, configId: number) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.aifeedbackDataUrl;

			let query = {
				caseid: caseId,
				configid: configId
			}
			this.http.post(apiURL, query)
				.subscribe({
					next: (res: any) => {
						resolve({ status: true, data: res });
					},
					error: (err: any) => {
						resolve({ status: false, data: {} })
					},
					complete: () => {

					},
				});
		});
		const result: any = await promise;
		return result;
	}
}
