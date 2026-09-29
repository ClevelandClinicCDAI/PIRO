import { Component } from '@angular/core';
// import { Store } from '@ngrx/store';
import { Observable, Subscription } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { SearchService } from '../../../services/search.service';
import { FilterService } from '../../../services/filter.service';
import { Common } from '../../../helpers';
import { ActivatedRoute, NavigationEnd, NavigationStart, ParamMap, Router } from '@angular/router';
import { TagComponent } from '../../modal/tag/tag.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SaveTagService } from '../../../services/save-tag.service';
// import { facetFilter, loadFilter } from '../../../store/result.actions';
import { LocalStorageService } from '../../../services/localStorage.service';
import { SynopticCopathComponent } from '../../common/synoptic-copath/synoptic-copath.component';
import { SynopticEpicComponent } from '../../common/synoptic-epic/synoptic-epic.component';
import { ToastrService } from 'ngx-toastr';
import { SendToExtractionComponent } from '../../modal/send-to-extraction/send-to-extraction.component';
@Component({
  standalone: false,
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent {
  page: number = 1;
  count: number = 0;
  countLimit: number = 0;
  tableSize: number = 5;
  content: any = [];

  filter: any = [];
  allFilterData: any = [];
  defaultSortBy: any = 'accessiondate';
  sortBy: any = this.defaultSortBy;
  contentLoaded = true;
  toggleDirective = true;
  subscription!: Subscription;
  skeltoncards: any = [1, 2, 3];
  searchProcessing: Boolean = false;
  filterRoute : string = '';
  dataFilterSubscription: any;
  sortFilterSubscription: any;

  resultPayloadSubscription:any;
  noResults: boolean = false;

  /** Cases selected for Extraction Suite */
  selectedCaseIds: Set<number> = new Set();
  constructor(private modalService: NgbModal, 
    private searchService: SearchService, 
    private common: Common, 
    // private store: Store<{ dataFilter: [], sortData: [], facetFilter: []}>, 
    private router: Router,
    private activatedRoute: ActivatedRoute, 
    private saveTagService: SaveTagService,
    private filterService:FilterService,
    private localStorageService:LocalStorageService,
    private toastr: ToastrService) { }
  ngOnInit() {
    this.filterRoute =  this.activatedRoute.snapshot.queryParams['searchFilter'];
    if (this.activatedRoute.snapshot.queryParams['searchFilter']) {
      this.activatedRoute.queryParamMap.subscribe((params: ParamMap) => {
        this.filter = JSON.parse(params.get('searchFilter') || '[]');
        this.page = parseInt(params.get('page') || '1');
        this.sortBy = (params.get('sortBy') !==  null) ? params.get('sortBy') : this.defaultSortBy;
        
        //Set Route Params in Local Storage
        this.localStorageService.setFilter(params.get('searchFilter'));
        this.localStorageService.setPage(this.page);
        this.localStorageService.setSortBy(this.sortBy);        
      });
     
      //called on page refresh and click from history
      this.content = [];
      this.count = 0;
      this.countLimit = 0;
      var advfilter = this.localStorageService.getAdancedFilterData();
      
      if ((this.filter.length > 0) || (JSON.stringify(advfilter) != '{}')) {
        this.getAll();
      }
    }
    
    this.resultPayloadSubscription = this.filterService.getResultPayload().subscribe((data: any) => {       
			if(data.status){        
        if(data.type == 'clearfilter'){
          this.filter = [];
          this.page = 1;
          this.content = [];
          this.sortBy = this.defaultSortBy;
          this.count = 0;
          this.countLimit = 0;
        }else{          
          this.filter  = data.filters;
          this.page = data.page;
          this.sortBy = (data.sortBy != '') ? data.sortBy : this.defaultSortBy;
          this.getAll();
        }
			}
		});

    this.sortFilterSubscription = this.filterService.getSortOrder().subscribe((data: any) => {
      if (data.status) {
        this.sortBy = (data.sortBy != '') ? data.sortBy : this.defaultSortBy; 
        this.getAll();
      }
    });

    //Tag save changes will trigger the data load
    this.subscription = this.saveTagService.getStatusCount().subscribe((data: any) => {
      if (data.status) {
        this.getAll();
      }
    });
  }


  ngOnDestroy(){
    this.filterService.setResultPayload([],1,'','',false);
    this.resultPayloadSubscription.unsubscribe();

		//this.dataFilterSubscription.unsubscribe();
    this.filterService.setSortOrder('',false);
    this.sortFilterSubscription.unsubscribe();
    this.subscription.unsubscribe();

    localStorage.removeItem('filter');
    localStorage.removeItem('page');
    localStorage.removeItem('sortBy');
	}


  async getAll() {    
      this.contentLoaded = false;       
      var searchUrlFrom = this.localStorageService.getSearchUrl();
      var searchUrlTo = "searchFilter=" + JSON.stringify(this.filter) + "&" +
        "page=" + this.page + "&" + "sortBy=" + this.sortBy;     

      //Update the route URL
      this.router.navigate([], {
          relativeTo: this.activatedRoute,
          queryParams: { searchFilter: JSON.stringify(this.filter), page: this.page, sortBy: this.sortBy },
          replaceUrl: true
      }).then(()=>{
        // do whatever you need after navigation succeeds
        localStorage.setItem("search-url", searchUrlTo);
        this.loadSearch();
      });
      
  }

  async loadSearch() {
    if(this.searchProcessing) {
      return;
    }    
    this.searchProcessing = true;
    this.content = [];
    this.noResults = false;
    var advFilter = this.localStorageService.getAdancedFilterData();
    var mrn = this.localStorageService.getMrn();
    const result = await this.searchService.getAll(this.page, this.tableSize, this.filter, advFilter, mrn, this.sortBy);
    if (result.status == true) {
      this.content = result.data?.items || [];
      this.noResults = this.content.length == 0;
      this.count = result.data?.total;
      this.countLimit = this.count > 100000 ? 100000 : this.count;
      this.contentLoaded = true;
      this.searchProcessing = false;
      this.tableSize = result.data?.size;

      for (var item of this.content) {
        if (item.synoptictexts?.length > 0) { 
            item.synopticreport = item.synoptictexts.some((str: string) => str.includes("#Synoptic Report#") || str.includes("||||"))
        }
      }
      


    } else {
      this.contentLoaded = true;
      this.searchProcessing = false;
      this.toastr.error('', 'Something went wrong.');
    }
  }

  convertDate(date: any) {
    return (date == null || date === '') ? "" : this.common.formatDateTime(date);
  }

  onTableDataChange(event: any) {
    this.page = event;
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: { searchFilter: JSON.stringify(this.filter), page: this.page, sortBy: this.sortBy },
      replaceUrl: true
    });
    this.getAll();
  }
  onTableSizeChange(event: any): void {
    this.tableSize = event.target.value;
    this.page = 1;
    this.getAll();
  }

  openTag(caseid: number, casenum: string) {
    const modalRef = this.modalService.open(TagComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true, backdrop: 'static', keyboard: false });
    modalRef.componentInstance.CaseId = caseid;
    modalRef.componentInstance.CaseNum = casenum;
    modalRef.result.then((result) => {

    }).catch((error) => {

    });
  }


  openConcentriqUrl(url: string) {
     window.open(url, "_blank");
  }

  opensynopticCopathModal(caseId: number) {
		const modalRef = this.modalService.open(SynopticCopathComponent, { ariaLabelledBy: 'modal-basic-title', size: 'xl', scrollable: true });    
    modalRef.componentInstance.caseId = caseId;
    modalRef.componentInstance.isModal = true;
   
		modalRef.result.then((result) => {    

		}).catch((error) => {
      if (error != "0") {
        console.log(error);
      }      
		});
	}

  opensynopticEpicModal(caseId: number) {
		const modalRef = this.modalService.open(SynopticEpicComponent, { ariaLabelledBy: 'modal-basic-title', size: 'xxl', scrollable: true });    
    modalRef.componentInstance.caseId = caseId;
    modalRef.componentInstance.isModal = true;
   
		modalRef.result.then((result) => {    

		}).catch((error) => {
      if (error != "0") {
        console.log(error);
      }      
		});
	}

  toggleCase(caseId: number) {
    if (this.selectedCaseIds.has(caseId)) {
      this.selectedCaseIds.delete(caseId);
    } else {
      this.selectedCaseIds.add(caseId);
    }
  }

  openSendToExtraction() {
    const modalRef = this.modalService.open(SendToExtractionComponent, {
      ariaLabelledBy: 'send-to-extraction-title',
      size: 'md',
      backdrop: 'static'
    });
    modalRef.componentInstance.caseIds = Array.from(this.selectedCaseIds);
    modalRef.result.then((sessionId) => {
      this.selectedCaseIds.clear();
    }).catch(() => {});
  }
}