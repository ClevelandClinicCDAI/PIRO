import { Component } from '@angular/core';
import { ConfirmDialogService } from '../../services/confirm-dialog.service';  

@Component({
  standalone: false,
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.css']
})
export class ConfirmDialogComponent {
  message: any;  
  constructor(private confirmDialogService: ConfirmDialogService) { }  

  ngOnInit(): any {
     /** 
      *   This function waits for a message from alert service, it gets 
      *   triggered when we call this from any other component 
      */  
      this.confirmDialogService.getMessage().subscribe(message => {  
          this.message = message;  
      });  
  }
}
