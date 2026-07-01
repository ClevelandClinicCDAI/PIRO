import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { EmailUsersService } from '../../../services/email-users.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-email-users',
  templateUrl: './email-users.component.html',
  styleUrls: ['./email-users.component.css']
})
export class EmailUsersComponent {
  emailForm!: FormGroup;
  submitted = false;
  sending = false;

  constructor(
    private fb: FormBuilder,
    private emailUsersService: EmailUsersService,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    this.emailForm = this.fb.group({
      subject: ['', [Validators.required, Validators.maxLength(500)]],
      body: ['', [Validators.required]],
      domain: ['', [Validators.required, Validators.maxLength(100)]]
    });
  }

  get f() { return this.emailForm.controls; }

  async onSubmit() {
    this.submitted = true;
    if (this.emailForm.invalid) return;

    this.sending = true;
    const { subject, body, domain } = this.emailForm.value;
    const result: any = await this.emailUsersService.sendEmail(subject, body, domain);
    this.sending = false;

    if (result?.status) {
      const count = result.data?.recipientCount ?? 0;
      this.toastr.success(`Email sent to ${count} user${count !== 1 ? 's' : ''}.`, 'Success');
      this.emailForm.reset();
      this.submitted = false;
    } else {
      this.toastr.error('Failed to send emails. Please try again.', 'Error');
    }
  }
}
