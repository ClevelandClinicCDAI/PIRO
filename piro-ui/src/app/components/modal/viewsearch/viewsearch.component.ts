import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { SavesearchService } from '../../../services/savesearch.service';

@Component({
  standalone: false,
  selector: 'app-viewsearch',
  templateUrl: './viewsearch.component.html',
  styleUrls: ['./viewsearch.component.css']
})
export class ViewsearchComponent {
  @Input() public SearchId:number = 0;
  data: any = {}
  display: string = ""
  constructor(
    private activeModal: NgbActiveModal, 
    private saveSearchService: SavesearchService,
    private toastr: ToastrService) {
		
	}

  ngOnInit() {
		this.getSearch();
	}

  async getSearch(){
    // console.log(this.SearchId);
		const result: any= await this.saveSearchService.getSearch(this.SearchId);
    // console.log(result);
		if(result.status == true){
		  this.data = result.data;
      this.display = this.data.display;
      this.display = this.display.replaceAll("#", "").replaceAll("$", "");
		}
	}

  closeModal() {
		this.activeModal.close('Modal Closed');		 
	}
}