import { Component, Input } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { Router } from '@angular/router';
import { FilterService } from '../../../services/filter.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { LocalStorageService } from '../../../services/localStorage.service';
@Component({
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

	constructor(
		private activeModal: NgbActiveModal,
		private authService: AuthService,
		private router: Router, private filterService: FilterService,private localStorageService: LocalStorageService) { }

	ngOnInit(): void {
		//this.requireAttest = false;
	}

	async attest(action: string) {
		if (action == "yes") {
			this.authService.saveAttestation().then(async (data: any) => {
				const resp = await this.authService.login(this.username, this.password, true);
				if(resp.status == true){
					this.filterService.setLogin(this.isAuth, this.role, this.status);
					this.activeModal.close('Modal Closed');
					this.router.navigate(['/search']);
				}
			});
		} else {
			const resp = await this.authService.login(this.username, this.password, false);
			if(resp.status == true){
				this.filterService.setLogin(this.isAuth, this.role, this.status);
				this.activeModal.close('Modal Closed');
				this.router.navigate(['/search']);
			}
		}
	}
}
