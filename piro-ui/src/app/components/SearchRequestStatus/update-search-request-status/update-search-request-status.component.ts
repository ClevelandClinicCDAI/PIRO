import { Component } from '@angular/core';
import { FormGroup,Validators,FormBuilder } from '@angular/forms';
import { SearchRequestStatusService } from '../../../services/search-request-status.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  standalone: false,
  selector: 'app-update-search-request-status',
  templateUrl: './update-search-request-status.component.html',
  styleUrls: ['./update-search-request-status.component.css']
})
export class UpdateSearchRequestStatusComponent {
  requestForm:any = FormGroup;
  submitted = false;
  id: any;
  constructor( private formBuilder: FormBuilder, private searchRequestStatusService:SearchRequestStatusService, private toastr: ToastrService,private router:Router,private route: ActivatedRoute){}
  get f() { return this.requestForm.controls; }

  async onSubmit() {
    this.submitted = true;
    
    // stop here if form is invalid
    if (this.requestForm.invalid) {
        return;
    }
    //True if all the fields are filled
    if(this.submitted) {
      const res:any = await this.searchRequestStatusService.update(this.requestForm.value);
      if(res.status == true){
        this.toastr.success('', 'Search request status updated successfully.');
        this.router.navigate(['search-request-status']);
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
      searchRequestStatusId:this.id,
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description:['',[Validators.required]],
      reference: ['', [Validators.required]]
    });
    const detail  = await this.searchRequestStatusService.getDetail(this.id);
    if(detail.status == true){
      this.requestForm.patchValue(detail.data);
    }
  }
}
