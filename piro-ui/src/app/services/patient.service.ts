import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class PatientService {
  constructor(private http: HttpClient) { } 

	async searchMrn(mrn: string) {
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl + 'patient/search/' + mrn;
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
		const result: any = await promise;
		return result;
	}

	 
}
