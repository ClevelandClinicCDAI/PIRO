import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { GenderService } from '../../../services/gender.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-update-gender',
  templateUrl: './update-gender.component.html',
  styleUrls: ['./update-gender.component.css']
})
export class UpdateGenderComponent {
  genderRequestForm:any = FormGroup;
  submitted = false;
  id: any;
  constructor( private formBuilder: FormBuilder, private genderService:GenderService, private toastr: ToastrService,private router:Router,private route: ActivatedRoute){}
  get f() { return this.genderRequestForm.controls; }

  async onSubmit() {
    this.submitted = true;
    
    // stop here if form is invalid
    if (this.genderRequestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.genderService.updateGender(this.genderRequestForm.value);
      if(res.status == true){
        this.toastr.success('', 'Gender updated successfully.');
        this.router.navigate(['sex']);
      }else if(res.status == false){
        this.toastr.error('',res.err);
      }else{
        this.toastr.error('','Something went wrong.');
      }
    }
  }
  
  async ngOnInit() {
    this.id = this.route.snapshot.params['id'];

    //Add Data Extract Request Form Validations
    this.genderRequestForm = this.formBuilder.group({
      genderId:this.id,
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      reference: ['', [Validators.required]]
    });
    const detail  = await this.genderService.getGenderDetail(this.id);
    if(detail.status == true){
      this.genderRequestForm.patchValue(detail.data);
    }
  }
}
