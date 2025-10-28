import { Component } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { CommentTypeService } from '../../../services/comment-type.service';
import { ToastrService } from 'ngx-toastr';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-update-comment-type',
  templateUrl: './update-comment-type.component.html',
  styleUrls: ['./update-comment-type.component.css']
})
export class UpdateCommentTypeComponent {
  requestForm: any = FormGroup;
  submitted = false;
  id: any;
  constructor(private formBuilder: FormBuilder, private commentTypeService: CommentTypeService, private toastr: ToastrService, private router: Router, private route: ActivatedRoute) { }
  get f() { return this.requestForm.controls; }

  async onSubmit() {
    this.submitted = true;

    // stop here if form is invalid
    if (this.requestForm.invalid) {
      return;
    }
    //True if all the fields are filled
    if (this.submitted) {
      const res: any = await this.commentTypeService.update(this.requestForm.value);
      if (res.status == true) {
        this.toastr.success('', 'Comment type updated successfully.');
        this.router.navigate(['comment-types']);
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
    this.requestForm = this.formBuilder.group({
      commentTypeId: this.id,
      display: ['', [Validators.required]],
      code: ['', [Validators.required]],
      description: ['', [Validators.required]],
      reference: ['', [Validators.required]],
      etlSource: ['', [Validators.required]]
    });
    const detail = await this.commentTypeService.getDetail(this.id);
    if (detail.status == true) {
      this.requestForm.patchValue(detail.data);
    }
  }
}
