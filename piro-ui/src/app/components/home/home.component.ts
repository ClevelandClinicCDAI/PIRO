import { Component } from '@angular/core';
import { AuditService } from '../../services/audit.service'
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { LocalStorageService } from '../../services/localStorage.service';
@Component({
  standalone: false,
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  isLoginin: boolean = false;
  items: any = [];
  loaded: boolean = false;
  isSearch: boolean = true;
  isAudit: boolean = false;
  constructor( private auditService:AuditService, 
    private toastr: ToastrService,
    private router:Router,
    private localStorageService:LocalStorageService){}
  ngOnInit(): void {
		//Add User form validations		 
		// if(localStorage.getItem('api-token')){
    if(this.localStorageService.getApiToken()){
			this.isLoginin = true;
		}
    this.getHistorySearch();
	}

  async getHistorySearch(){
    const result = await this.auditService.getHistoryLatest();
    if(result.status == true){
      this.items = result.data;
      this.loaded = true;     
    } else {
      this.loaded = true;
    }
  }

  transform(input: string, inputAdv: string, mrn: string): string {    
    var searchRegExp = /##/g;
    var replaceWith = '<span class="form-item"><span class="bg-primary filteritem"><span class="filterDisplayName">';
    input = input.replace(searchRegExp, replaceWith);
    searchRegExp = /\$\$/g;
    replaceWith = '</span></span></span>';
    input = input.replace(searchRegExp, replaceWith);
    if ((inputAdv || '') != '') {
      input = input + '<span class="form-item"><span class="bg-primary filteritem advfilteritem"><span>' + 
      inputAdv + replaceWith;
    }
    if ((mrn || '') != '') {
      input = input + '<span class="form-item"><span class="bg-primary filteritem mrnfilteritem"><span>' + 
      mrn + replaceWith;
    }
    return input;
  }

  assignAdvSearch(advSearch: any, mrn: any, url: any) {    
    this.localStorageService.setAdancedFilterData(JSON.parse(advSearch));
    if((mrn || '') != '') {
      this.localStorageService.setMrn(mrn);
    }
    // console.log(url);
    this.router.navigateByUrl(url);
  }
}
