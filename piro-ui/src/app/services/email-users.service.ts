import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EmailUsersService {
  private baseUrl = environment.apiBaseUrl + 'email-users';

  constructor(private http: HttpClient) {}

  sendEmail(subject: string, body: string, domain: string) {
    return new Promise((resolve) => {
      this.http.post<any>(`${this.baseUrl}/send`, { subject, body, domain }).subscribe({
        next: (res: any) => resolve({ status: true, data: res }),
        error: (err: any) => resolve({ status: false, err })
      });
    });
  }
}
