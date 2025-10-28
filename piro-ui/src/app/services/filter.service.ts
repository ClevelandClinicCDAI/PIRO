import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { LocalStorageService } from '../services/localStorage.service';

@Injectable({
  providedIn: 'root'
})
export class FilterService {

  constructor(private localStorageService: LocalStorageService) { }

  private getFacetFromFilterData = new BehaviorSubject<any>({
    facets: [],
    status: false
  });
  private getFacetFromFilterData$ = this.getFacetFromFilterData.asObservable();


  getFacetFromFilterDataArr(): Observable<any> {
    return this.getFacetFromFilterData$;
  }

  setFacetFromFilterDataArr(value: any, status: boolean = true) {
    return this.getFacetFromFilterData.next({ facets: value, status: status });
  }

  private getFilterFacetData = new BehaviorSubject<any>({
    filters: [],
    page: 1,
    sortBy: '',
    status: false,
    type: ''
  });
  private getFilterFacetData$ = this.getFilterFacetData.asObservable();


  private getFilterFacetMrnData = new BehaviorSubject<any>({    
    status: false    
  });
  private getFilterFacetMrnData$ = this.getFilterFacetMrnData.asObservable();


  getFilterForFacetArr(): Observable<any> {
    return this.getFilterFacetData$;
  }

  getFilterForFacetMrnArr(): Observable<any> {
    return this.getFilterFacetMrnData$;
  }

  setFilterForFacetMrnArr() {
    return this.getFilterFacetMrnData.next({ status: true });
  }

  setFilterForFacetArr(filterItem: any, checked: boolean, type: string, status: boolean = true) {
    // var filter = JSON.parse(localStorage.getItem('filter') || '[]');
    // var page   = parseInt(localStorage.getItem('page') || '1');
    // var sortBy = localStorage.getItem('sortBy') || 'accessiondate';
    var filter = this.localStorageService.getFilter();
    var page = this.localStorageService.getPage();
    var sortBy = this.localStorageService.getSortBy();

    if (type == 'clearfilter') {
      filter = [];
      page = 1;
      sortBy = 'accessiondate';
    } else if (type == 'refreshfilter') {
      //pass the filter values from storage
    } else {
      if (filterItem) {
        page = 1;
        //If data is checked (added)   
        if (checked) {
          //Remove the patient age filter and isdeceased filter
          filter.forEach((element: any, i: number) => {
            if (filterItem.field === element.field && element.field === 'casepatientageyears') {
              filter.splice(i, 1);
            }
            if (filterItem.field === element.field && element.field === 'isdeceased') {
              filter.splice(i, 1);
            }
            if (filterItem.field === element.field && element.field === 'isconcentriq') {
              filter.splice(i, 1);
            }            
          });
          //Facet
          if (filter.length > 0) {
            filter.forEach((element: any, i: number) => {
              if (filterItem?.type != undefined) {
                if (filterItem.field === element.field) {
                  filter.splice(i, 1);
                }
              }
            });
          }
          //Filter dropdown 
          if (filterItem.search != '') {
            if (filter.length > 0) {
              filter.forEach((element: any, i: number) => {
                if (filterItem?.type == undefined) {
                  if (filterItem.field === element.field && filterItem.search == element.search) {
                    filter.splice(i, 1);
                  }
                } else {
                  if (filterItem.field === element.field) {
                    filter.splice(i, 1);
                  }
                }
              });
            }
            filter.push(filterItem);
          } else if (filterItem.search == '') {
            var index = filter.findIndex(function (v: any, i: number) {
              return v.field === filterItem.field && v.andcondition == true;
            });
            filter.splice(index, 1);
          }
        } else {
          //If Data is unchecked/removed
          var index = filter.findIndex(function (v: any, i: number) {
            // return v.search === filterItem.search && v.andcondition == false;
            return v.search === filterItem.search && v.category == filterItem.category;
          });
          filter.splice(index, 1);
        }
      } else {
        filter = [];
        page = 1;
        sortBy = 'accessiondate';
      }
    }
    this.localStorageService.setFilter(filter);
    return this.getFilterFacetData.next({ filters: filter, page: page, sortBy: sortBy, status: status, type: type });
  }

  private getResultPayloadData = new BehaviorSubject<any>({
    filters: [],
    page: 1,
    sortBy: '',
    status: false,
    type: ''
  });
  private getResultPayloadData$ = this.getResultPayloadData.asObservable();


  getResultPayload(): Observable<any> {
    return this.getResultPayloadData$;
  }

  setResultPayload(filters: any, page: any, sortBy: string, type: string, status: boolean = false) {
    return this.getResultPayloadData.next({ filters: filters, page: page, sortBy: sortBy, status: status, type: type });
  }

  private getSortOrderData = new BehaviorSubject<any>({
    sortBy: '',
    status: false
  });
  private getSortOrderData$ = this.getSortOrderData.asObservable();


  getSortOrder(): Observable<any> {
    return this.getSortOrderData$;
  }

  setSortOrder(sortBy: string, status: boolean = false) {
    return this.getSortOrderData.next({ sortBy: sortBy, status: status });
  }


  private getLoginData = new BehaviorSubject<any>({
    role: '',
    isAuth: false,
    status: false
  });
  private getLoginData$ = this.getLoginData.asObservable();


  getLogin(): Observable<any> {
    return this.getLoginData$;
  }

  setLogin(isAuth: boolean, role: string, status: boolean = false) {
    return this.getLoginData.next({isAuth: isAuth, role: role, status: status });
  }
}
