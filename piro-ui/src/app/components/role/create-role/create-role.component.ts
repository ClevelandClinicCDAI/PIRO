import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { RoleService } from '../../../services/role.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-role',
  templateUrl: './create-role.component.html',
  styleUrls: ['./create-role.component.css']
})
export class CreateRoleComponent {
  requestForm:any = FormGroup;
  submitted = false;
  constructor( private formBuilder: FormBuilder, private roleService:RoleService, private toastr: ToastrService,private router:Router){}
  get f() { return this.requestForm.controls; }

  async onSubmit() {  
    this.submitted = true;
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.roleService.createRole(this.requestForm.value);
      
      if(res.status == true){
        this.toastr.success('', 'Role added successfully.');
        this.router.navigate(['roles']);
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
