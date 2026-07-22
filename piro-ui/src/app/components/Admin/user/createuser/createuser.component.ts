import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-createuser', 
  templateUrl: './createuser.component.html',
  styleUrls: ['./createuser.component.css']
})
export class CreateuserComponent {
  userRequestForm:any = FormGroup;
  submitted = false;
  roles:any = [];
  constructor( private formBuilder: FormBuilder, private userService:UserService, private roleService:RoleService, private toastr: ToastrService,private router:Router){}
  get f() { return this.userRequestForm.controls; }

  async onSubmit() {  
    this.submitted = true;
    // stop here if form is invalid
    if (this.userRequestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      this.userRequestForm.controls['roleId'].setValue(parseInt(this.userRequestForm.get('roleId').value));
      const res:any = await this.userService.createUser(this.userRequestForm.value);
      if(res.status == true){
        this.toastr.success('', 'User added successfully.');
        this.router.navigate(['adminuser']);
      }else if(res.status == false){
        this.toastr.error('',res.err);
      }else{
        this.toastr.error('','Something went wrong.');
      }
    }
  }
  
  async ngOnInit() {
    //Add Data Extract Request Form Validations
    this.userRequestForm = this.formBuilder.group({
      nuid: ['', [Validators.required]],
      firstName: ['', [Validators.required]],
      lastName:['',[Validators.required]],
      roleId: ['', [Validators.required]]
    });
    this.roles = await this.roleService.getRolesDropdown(); 
  }

}
