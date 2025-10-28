import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
	providedIn: 'root'
})
export class AivoteService {
	constructor(private http: HttpClient) { }

	saveIntoDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.saveaivoteUrl;
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

	async saveVote(data: any) {
		return await this.saveIntoDB(data);
	}

	markReviewedIntoDB(annotationCaseFeedbackId: number) {
		let data = {
			annotationCaseFeedbackId: annotationCaseFeedbackId
		}
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.markreviewedUrl;
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

	async markReviewed(data: any) {
		return await this.markReviewedIntoDB(data);
	}

	getAIVoteReviewsFromDB(data: any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.aifeedbackCaseUrl;
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

	async getAIVoteReviews(data: any) {
		return await this.getAIVoteReviewsFromDB(data);
	}

	getAllFromDB(page: number, size: number, data : any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.aifeedbackAllUrl;
			data.page = page;
			data.size = size;
			let query = {
				params: data
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

	async getAll(page: number, size: number, data: any) {
		const result: any = await this.getAllFromDB(page, size, data);
		return result;
	}


 

	isPending() {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.isPendingAiFeedbackReviewUrl;
			 
			let query = {}
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


	getAuditFromDB(data : any) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + environment.aicaseauditlUrl;
			this.http.post(apiURL, data)
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

	async getAudit(data: any) {
		const result: any = await this.getAuditFromDB(data);
		return result;
	}
}
