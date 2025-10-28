import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { EthnicityService } from '../../../services/ethnicity.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-update-ethnicity',
  templateUrl: './update-ethnicity.component.html',
  styleUrls: ['./update-ethnicity.component.css']
})
export class UpdateEthnicityComponent {
  requestForm:any = FormGroup;
  submitted = false;
  id: any;
  constructor( private formBuilder: FormBuilder, private ethnicityService:EthnicityService, private toastr: ToastrService,private router:Router,private route: ActivatedRoute){}
  get f() { return this.requestForm.controls; }

  async onSubmit() {
    this.submitted = true;
    
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.ethnicityService.update(this.requestForm.value);
      if(res.status == true){
        this.toastr.success('', 'Ethnicity updated successfully.');
        this.router.navigate(['ethnicity']);
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
    this.requestForm = this.formBuilder.group({
      ethnicityId:this.id,
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      reference: ['', [Validators.required]]
    });
    const detail  = await this.ethnicityService.getDetail(this.id);
    if(detail.status == true){
      this.requestForm.patchValue(detail.data);
    }
  }
}
