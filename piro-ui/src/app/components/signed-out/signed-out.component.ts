import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
    standalone: false,
    selector: 'app-signed-out',
    template: `
    <div class="container mt-5">
      <div class="row-fluid">
        <div class="col-md-6" style="float:none;margin:auto;">
          <div class="card shadow p-4 bg-white rounded text-center">
            <h4 class="mb-3">You are signed out</h4>
            <p class="text-muted mb-4">
              Your PIRO session has ended. Choose an option below.
            </p>
            <div class="d-grid gap-2 d-md-block">
              <button type="button" class="btn btn-primary me-md-2" (click)="signInAgain()">
                Sign in again
              </button>
              <button type="button" class="btn btn-outline-secondary" (click)="goToLoginPage()">
                Go to login page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class SignedOutComponent {
    constructor(private router: Router) { }

    signInAgain(): void {
        this.router.navigate(['/login']);
    }

    goToLoginPage(): void {
        this.router.navigate(['/login'], {
            queryParams: { signedOut: '1', manual: '1' },
        });
    }
}
