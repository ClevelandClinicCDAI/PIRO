import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { EthnicityService } from '../../../services/ethnicity.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-create-ethnicity',
  templateUrl: './create-ethnicity.component.html',
  styleUrls: ['./create-ethnicity.component.css']
})
export class CreateEthnicityComponent {
  requestForm:any = FormGroup;
  submitted = false;
  constructor( private formBuilder: FormBuilder, private ethnicityService:EthnicityService, private toastr: ToastrService,private router:Router){}
  get f() { return this.requestForm.controls; }

  async onSubmit() {  
    this.submitted = true;
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.ethnicityService.create(this.requestForm.value);
      
      if(res.status == true){
        this.toastr.success('', 'Ethnicity added successfully.');
        this.router.navigate(['ethnicity']);
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
