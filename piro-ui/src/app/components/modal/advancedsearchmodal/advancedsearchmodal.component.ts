import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder } from '@angular/forms';
//import { QueryBuilderClassNames, QueryBuilderConfig } from 'angular2-query-builder';
import { QueryBuilderClassNames, QueryBuilderConfig } from '../../../angular2-query-builder/src/lib/query-builder/query-builder.interfaces';
import { SearchService } from '../../../services/search.service';
import { LocalStorageService } from '../../../services/localStorage.service';
import { ToastrService } from 'ngx-toastr';
import { ConfirmDialogService } from '../../../services/confirm-dialog.service';
@Component({
  selector: 'app-advancedsearchmodal',
  templateUrl: './advancedsearchmodal.component.html',
  styleUrls: ['./advancedsearchmodal.component.css']
})
export class AdvancedsearchmodalComponent implements OnInit {
  // @Input() id!: number; 
  constructor(private activeModal: NgbActiveModal, 
    private searchService: SearchService,
    private localStorage: LocalStorageService,
    private toastr: ToastrService,
    private confirmDialogService: ConfirmDialogService) {
  }

  classNames: QueryBuilderClassNames = {
    removeIcon: 'fa fa-minus remove-icon',
    addIcon: 'fa fa-plus',
    button: 'btn btn-primary btn-ruleset',
    buttonGroup: 'btn-group',
    switchLabel: 'btn q-switch-label',
  }

  config: QueryBuilderConfig = {
    fields: {
      "casenumber": {
          "name": "Case Number",
          "type": "string",
          "operators": [
              "="
          ]
      }
    }
  }
  
  query = {
    condition: "and",
    rules: [{"field":"final","operator":"contains"}]
  };

 

  dataloaded: boolean = false;
  // isValid: boolean = false;
  isDisabled: boolean = false;
  async ngOnInit() {
    const result: any = await this.searchService.getAdvancedFilter();
    if (result.status == true) {
      this.config.fields = result.data;
      this.dataloaded = true;       
    }
    var advFilter = this.localStorage.getAdancedFilterData();
    if (JSON.stringify(advFilter) != '{}' && JSON.stringify(advFilter) != '') {
      this.query = advFilter;
    }
  }

  saveModal() {
    this.localStorage.setAdancedFilterData(this.query);
    this.activeModal.close(true);
  }

  closeModal() {
    this.activeModal.close(false);
  }

  windowEvent(event:any){
		if(event.keyCode===13){
		  this.validateModal();
      event.preventDefault();
		}
	}

  async validateModal() {   
    this.isDisabled = true;
    const result: any = await this.searchService.validateAdvancedFilter(this.query);
    if (result.status == true) {
      let that = this;
      if(result.data.result) {        
        this.saveModal();
      } else {
        let that = this;
        this.confirmDialogService.alertCustom("Validation failed. Please correct the below errors <br/><li>" + result.data.message + "</li>", 'alert alert-danger', 'OK', 
        async function () {          
          that.isDisabled = false;
        });        
      }     
    } else {
      this.toastr.error('', 'Something went wrong.');
    }
  }
} 
