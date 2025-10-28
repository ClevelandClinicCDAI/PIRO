import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { ToastService } from '../../services/toast.service';
import { LocalStorageService } from '../../services/localStorage.service';
import { FilterService } from '../../services/filter.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { UserattestComponent } from '../modal/userattest/userattest.component';
import { ToastrService } from 'ngx-toastr';
declare var $: any;
@Component({
	selector: 'app-login',
	templateUrl: './login.component.html',
	styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
	loginForm: any = FormGroup;
	submitted = false;
	constructor(private formBuilder: FormBuilder,
		private authService: AuthService,
		private toastService: ToastService,
		private router: Router,
		private filterService:FilterService,
		private localStorageService:LocalStorageService,
		private modalService: NgbModal,
		private toastr: ToastrService) { }

	get f() { return this.loginForm.controls; }

	async onSubmit() {
		this.submitted = true;
		// stop here if form is invalid
		if (this.loginForm.invalid) {
			return;
		}
		//True if all the fields are filled
		if (this.submitted) {
			const resp = await this.authService.login(this.loginForm.get('username').value, this.loginForm.get('password').value, true);
			if(resp.status == true){
				console.clear();
				//Open popup
				this.authService.getAttestation().then(async (data: any) => {
					if (!data.isAttest && data.enabled) {
						this.openAttestPopup(resp.status, resp.role, true, data.textAttest, data.requireAttest, this.loginForm.get('username').value, this.loginForm.get('password').value);
					} else {
						const resp = await this.authService.login(this.loginForm.get('username').value, this.loginForm.get('password').value, false);
						if(resp.status == true){
							this.filterService.setLogin(resp.status, resp.role, true);
							this.router.navigate(['/search']);
						}
					}
				});

				//this.filterService.setLogin(resp.status, resp.role, true);
				//this.router.navigate(['/search']);
			} else {
				this.toastService.showErrorToast('Error', "Invalid credentials", []);
			}
		}
	}

	ngOnInit(): void {
		//Add User form validations
		this.loginForm = this.formBuilder.group({
			username: ['', [Validators.required]],
			password: ['', [Validators.required]]
		});
		// if(localStorage.getItem('api-token')){
		if(this.localStorageService.getApiToken()){
			this.router.navigate(['/home']);
		}
	}

	openAttestPopup(isAuth: boolean, role: string, status: boolean, textAttest: string, requireAttest: boolean, username: string, password: string) {
		const modalRef = this.modalService.open(UserattestComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true, backdrop: 'static', keyboard: false });

		modalRef.componentInstance.isAuth = isAuth;
		modalRef.componentInstance.role = role;
		modalRef.componentInstance.status = status;
		modalRef.componentInstance.textAttest = textAttest;
		modalRef.componentInstance.requireAttest = requireAttest;
		modalRef.componentInstance.username = username;
		modalRef.componentInstance.password = password;

		modalRef.result.then((result) => {

		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}
}
