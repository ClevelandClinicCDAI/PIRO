import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { SpecimenSourceService } from '../../../services/specimen-source.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
  selector: 'app-update-specimen-source',
  templateUrl: './update-specimen-source.component.html',
  styleUrls: ['./update-specimen-source.component.css']
})
export class UpdateSpecimenSourceComponent {
  requestForm:any = FormGroup;
  submitted = false;
  id: any;
  constructor( private formBuilder: FormBuilder, private specimenSourceService:SpecimenSourceService, private toastr: ToastrService,private router:Router,private route: ActivatedRoute){}
  get f() { return this.requestForm.controls; }

   
  async ngOnInit() {
    this.id = this.route.snapshot.params['id'];

    //Add Data Extract Request Form Validations
    this.requestForm = this.formBuilder.group({
      specimenSourceId:this.id,
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      score:['',[Validators.nullValidator]],
      reference: ['', [Validators.required]]
    });
    const detail  = await this.specimenSourceService.getSpecimenSourceDetail(this.id);
    if(detail.status == true){
      this.requestForm.patchValue(detail.data);
    }
  }

  async onSubmit() {
    this.submitted = true;
    
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.specimenSourceService.updateSpecimenSource(this.requestForm.value);
      if(res.status == true){
        this.toastr.success('', 'Specimen source updated successfully.');
        this.router.navigate(['specimen-sources']);
      }else if(res.status == false){
        this.toastr.error('',res.err);
      }else{
        this.toastr.error('','Something went wrong.');
      }
    }
  }
}
