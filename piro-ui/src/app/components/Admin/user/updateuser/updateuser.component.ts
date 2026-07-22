import { Component } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';
@Component({
  standalone: false,
  selector: 'app-updateuser',
  templateUrl: './updateuser.component.html',
  styleUrls: ['./updateuser.component.css']
})
export class UpdateuserComponent {
  userRequestForm: any = FormGroup;
  submitted = false;
  id: any;
  roles: any = [];
  detail: any;
  idRole: any;
  constructor(private formBuilder: FormBuilder, private userService: UserService, private roleService: RoleService,
    private toastr: ToastrService, private router: Router, private route: ActivatedRoute) { }
  get f() { return this.userRequestForm.controls; }

  async onSubmit() {
    this.submitted = true;

    // stop here if form is invalid
    if (this.userRequestForm.invalid) {
      return;
    }
    //True if all the fields are filled
    if (this.submitted) {
      // this.userRequestForm.controls['roleId'].setValue(parseInt(this.userRequestForm.get('roleId').value));
      const res: any = await this.userService.updateUser(this.userRequestForm.value);
      if (res.status == true) {
        this.toastr.success('', 'User updated successfully.');
        this.router.navigate(['adminuser']);
      } else if (res.status == false) {
        this.toastr.error('', res.err);
      } else {
        this.toastr.error('', 'Something went wrong.');
      }
    }
  }

  async ngOnInit() {
    this.id = this.route.snapshot.params['id'];

    //Add Data Extract Request Form Validations
    this.userRequestForm = this.formBuilder.group({
      userId: this.id,
      nuid: ['', [Validators.required]],
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      roleId: ['', [Validators.required]]
    });
    this.roles = await this.roleService.getRolesDropdown();
    this.detail = await this.userService.getUserDetail(this.id);
    this.idRole = this.detail.data.roleId;
    if (this.detail.status == true) {
      this.userRequestForm.patchValue(this.detail.data);
      // this.userRequestForm.controls['roleId'].setValue(this.detail.data.roleid);
    }
  }
}
