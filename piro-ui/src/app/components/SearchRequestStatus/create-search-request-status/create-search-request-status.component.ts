import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { SearchRequestStatusService } from '../../../services/search-request-status.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-create-search-request-status',
  templateUrl: './create-search-request-status.component.html',
  styleUrls: ['./create-search-request-status.component.css']
})
export class CreateSearchRequestStatusComponent {
  requestForm:any = FormGroup;
  submitted = false;
  constructor( private formBuilder: FormBuilder, private searchRequestStatusService:SearchRequestStatusService, 
    private toastr: ToastrService, private router:Router){}
  get f() { return this.requestForm.controls; }

  async onSubmit() {  
    this.submitted = true;
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.searchRequestStatusService.create(this.requestForm.value);
      
      if(res.status == true){
        this.toastr.success('', 'Search request status added successfully.');
        this.router.navigate(['search-request-status']);
      }else if(res.status == false){
        this.toastr.error('',res.err);
      }else{
        this.toastr.error('','Something went wrong.');
      }
    }
  }
  
  ngOnInit(): void {
    //Add Data Extract Request Form Validations
    this.requestForm = this.formBuilder.group({
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      reference: ['', [Validators.required]]
    });
  }
}
