import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { GenderService } from '../../../services/gender.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-creategender',
  templateUrl: './creategender.component.html',
  styleUrls: ['./creategender.component.css']
})
export class CreategenderComponent {
  genderRequestForm:any = FormGroup;
  submitted = false;
  constructor( private formBuilder: FormBuilder, private genderService:GenderService, private toastr: ToastrService,private router:Router){}
  get f() { return this.genderRequestForm.controls; }

  async onSubmit() {  
    this.submitted = true;
    // stop here if form is invalid
    if (this.genderRequestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      // const formData: FormData = new FormData();  
      // formData.set('code', this.genderRequestForm.get('name').value);
      // formData.set('description', this.genderRequestForm.get('description').value);
      // formData.set('reference', this.genderRequestForm.get('saved_search_option').value);
      const res:any = await this.genderService.createGender(this.genderRequestForm.value);

      if(res.status == true){
        this.toastr.success('', 'Sex added successfully.');
        this.router.navigate(['sex']);
      }else if(res.status == false){
        this.toastr.error('',res.err);
      }else{
        this.toastr.error('','Something went wrong.');
      }
    }
  }
  
  ngOnInit(): void {
    //Add Data Extract Request Form Validations
    this.genderRequestForm = this.formBuilder.group({
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      reference: ['', [Validators.required]]
    });
  }
}
