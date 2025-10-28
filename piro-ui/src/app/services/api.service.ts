import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) { }

  dataRequest(data:any){
  
  }

  updatePreference(data:any){
   
  }

  getUsersFromDB(){
		let promise = new Promise((resolve, reject) => {
			let apiURL = environment.apiBaseUrl+'user/all';
			this.http.get(apiURL)
			  .subscribe({
				next: (res: any) => {
					resolve({status:true,data:res});
				},
				error: (err: any) => {
					resolve({status:false,data:[]})
				},
				complete: () => {

				},
			});
		});
		return promise;
	}

  async getUsers(){
    const result:any = await this.getUsersFromDB();
		return result;
  }

  

  getEtlLogs(){
    const result = [
      {
        'activity': 'Change Status',
        'error_code': '400',
        'message':'Server Error',
        'created_at':'04/13/2023 04:10 AM'
      },
      {
        'activity': 'Get Users',
        'error_code': '400',
        'message':'Server Error',
        'created_at':'04/13/2023 04:15 AM'
      }
    ]
    return {'status':true,data: result }
  }

  getRequestHistory(){
    const result = [
      {
        'name': 'Test 1',
        'description': 'Test Message',
        'search_option':'Option 1',
        'file':'test.csv',
        'created_at':'04/13/2023 04:10 AM'
      },
      {
        'name': 'Test 2',
        'description': 'Test Message',
        'search_option':'Option 2',
        'file':'test.csv',
        'created_at':'04/13/2023 04:10 AM'
      }
    ]
    return {'status':true,data: result }
  }

  getUserHistory(){
    const result = [
      {
        'name': 'John Doe',
        'email': 'j@gmail.com',
        'department':'D1',
        'created_at':'04/13/2023 04:10 AM'
      },
      {
        'name': 'John',
        'email': 'jf@gmail.com',
        'department':'D2',
        'created_at':'04/13/2023 04:10 AM'
      }
    ]
    return {'status':true,data: result }
  }
}
