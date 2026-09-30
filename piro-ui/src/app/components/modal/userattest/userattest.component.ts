import { Component, Input } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { Router } from '@angular/router';
import { FilterService } from '../../../services/filter.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { LocalStorageService } from '../../../services/localStorage.service';
@Component({
	standalone: false,
	selector: 'app-userattest',
	templateUrl: './userattest.component.html',
	styleUrls: ['./userattest.component.css']
})
export class UserattestComponent {

	@Input() isAuth: boolean = false;
	@Input() status: boolean = false;
	@Input() requireAttest: boolean = false;
	@Input() role: string = "";
	@Input() textAttest: string = "";
	@Input() username: string = "";
	@Input() password: string = "";
	// Set by the OAuth callback instead of username/password.
	@Input() idToken: string = "";
	@Input() returnUrl: string = "/search";

	constructor(
		private activeModal: NgbActiveModal,
		private authService: AuthService,
		private router: Router, private filterService: FilterService, private localStorageService: LocalStorageService) { }

	ngOnInit(): void {
		//this.requireAttest = false;
	}

	async attest(action: string) {
		const accepted = action == "yes";
		if (accepted) {
			await this.authService.saveAttestation();
		}
		// Re-issue the PIRO token so its isAttest claim reflects the decision.
		const resp = await this.reissueToken(accepted);
		if (resp.status == true) {
			this.filterService.setLogin(this.isAuth, this.role, this.status);
			this.activeModal.close('Modal Closed');
			this.router.navigateByUrl(this.returnUrl);
		}
	}

	private reissueToken(islog: boolean) {
		return this.idToken
			? this.authService.loginWithIdToken(this.idToken, islog)
			: this.authService.login(this.username, this.password, islog);
	}
}
