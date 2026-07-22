import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { UserService } from '../../../services/user.service';

@Component({
  standalone: false,
  selector: 'app-preference',
  templateUrl: './preference.component.html',
  styleUrls: ['./preference.component.css']
})
export class PreferenceComponent {
  preferenceForm:any = FormGroup;
  submitted = false;
  constructor( private formBuilder: FormBuilder, private userService:UserService){}
  get f() { return this.preferenceForm.controls; }

  onSubmit() {
    this.submitted = true;
    // stop here if form is invalid
    if (this.preferenceForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted){
      this.userService.updatePreference(this.preferenceForm.value);
    }
  }

  async ngOnInit() {
    //Add form validations
    this.preferenceForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required,Validators.email]],
      department:['', [Validators.required]],
      is_persist: [0]
    });
    // const detail  = await this.userService.getUserDetail(0);
    // if(detail.status == true){
    //   this.preferenceForm.patchValue(detail.data);
    // }
  }
}
