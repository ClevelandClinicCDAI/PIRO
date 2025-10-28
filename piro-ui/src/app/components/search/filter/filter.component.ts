import { Component } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AdvancedsearchmodalComponent } from '../../modal/advancedsearchmodal/advancedsearchmodal.component';
import { SavesearchmodalComponent } from '../../modal/savesearchmodal/savesearchmodal.component';
import { SavedsearchcontentmodalComponent } from '../../modal/savedsearchcontentmodal/savedsearchcontentmodal.component';
import { SearchService } from '../../../services/search.service';
import { FilterService } from '../../../services/filter.service';
import { Subject, Subscription, debounceTime } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Store } from '@ngrx/store';
import { loadFacets, loadFilter, loadAutoSuggest, loadSortBy } from '../../../store/result.actions';
import { ActivatedRoute, ParamMap, Router, Event, NavigationStart, NavigationEnd, NavigationError } from '@angular/router';
import { LocalStorageService } from '../../../services/localStorage.service';
import { ToastrService } from 'ngx-toastr';
import { Options } from "@angular-slider/ngx-slider";
import { Common } from '../../../helpers/common';
import { MrnModalComponent } from '../../modal/mrn-modal/mrn-modal.component';
@Component({
	selector: 'app-filter',
	templateUrl: './filter.component.html',
	styleUrls: ['./filter.component.css'],
})
export class FilterComponent {
	minValue: number = 0;
	maxValue: number = 100;
	options: Options = {
		floor: 0,
		ceil: 100
	};
	subscription!: Subscription;
	mrnsubscription!: Subscription;
	filterTermClear: string = 'clearfilter';
	filterTermData: string = 'filter';

	closeResult = '';
	items: any = [];
	filterItems: any = [];
	showSearchInput: boolean = true;
	showTextInput: boolean = true;
	showDropdown: boolean = false;
	showRangeSlider: boolean = false;
	filterDropdownOptions: any = [];
	filterDropdown: string = '';
	displaysingular: string = '';
	searchInput: string = '';
	sortByText: string = 'Accession Date';
	filterSubject: any;
	searchKeyword: any = '';
	filterCatDropdown: string = '';
	filter: any = [];
	showAutoSuggest: boolean = false;
	clearFilterClass: string = '';
	showDateRange: boolean = false;

	// defaultFrom = new Date();
	// defaultTo = new Date(this.defaultFrom.getTime() + 2 * 24 * 60 * 60 * 1000);

	defaultFrom: string = '';
	defaultTo: string = '';

	placeholder: string = "";
	isMrn: boolean = true;
	constructor(private modalService: NgbModal,
		private searchService: SearchService,
		private store: Store<{ facets: [], dataFilter: [] }>,
		private router: Router, private common: Common,
		private activatedRoute: ActivatedRoute,
		private filterService: FilterService,
		private toastr: ToastrService,
		private localStorageService: LocalStorageService) {

	}

	ngOnInit() {
		//this.assignFiltersContent();

		//To get the filter dropdown
		this.getFilterMetaData(true);

		this.filterSubject = new Subject<String>();
		this.filterSubject.pipe(debounceTime(environment.debounceTime)).subscribe((value: String) => {
			this.callFilterStore(this.searchKeyword, this.filterTermData);
		});

		//Update in the route, reassign the filters
		this.router.events.subscribe((event: Event) => {
			if (event instanceof NavigationStart) { }
			if (event instanceof NavigationEnd) {
				// Hide loading indicator
				this.assignFiltersContent();
			}
			if (event instanceof NavigationError) {
				// Hide loading indicator
				// Present error to user
			}
		});

		this.subscription = this.searchService.getStatusCount().subscribe((data: any) => {
			if (data.status) {
				this.showAutoSuggest = false;
				const keyword = data.value;
				this.searchKeyword = keyword;
				this.filterSubject.next();
			} else {
				this.showAutoSuggest = false;
			}
		});


		this.mrnsubscription = this.filterService.getFilterForFacetArr().subscribe((data: any) => {
			if (data.status) {
				this.assignFiltersContent();
			}
		});

	}

	assignFiltersContent() {
		// var filter = JSON.parse(localStorage.getItem('filter') || '[]');
		var filter = this.localStorageService.getFilter();
		this.filter = filter.sort((a, b) => a.search.localeCompare(b.search)).sort((a, b) => a.category.localeCompare(b.category));
		var filterData = this.localStorageService.getFilterData();
		this.filter.forEach(function (item: any) {
			var filters = filterData.filter((filterItem: any) => filterItem.value === item.field);
			if (filters.length > 0) {
				item.title = filters[0].name;
				item.color = filters[0].color;
			}
		});
		//Add Advanced Search
		var advfilter = this.localStorageService.getAdancedFilterData();
		if (JSON.stringify(advfilter) != '{}') {
			this.filter.push({
				"type": "advfilter",
				"field": "advfilter",
				"search": "Advanced Filter",
				"category": "advfilter",
				"andcondition": false,
				"title": "Advanced Search",
				"text": "Advanced Search",
				"color": "#0047AB"
			});
		}

		var advmrn = this.localStorageService.getMrn();
		if (advmrn != '') {
			this.filter.push({
				"type": "advmrn",
				"field": "advmrn",
				"search": "MRN",
				"category": "advmrn",
				"andcondition": false,
				"title": "MRN Search",
				"color": "#6495ED"
			});
		}

		if (filter.length > 0) {
			this.filterDropdown = '';
			this.displaysingular = '';
			if (this.items instanceof Array) {
				const newArray = this.items.map((element: any) => {
					var index = filter.findIndex(function (v: any, i: number) {
						return v.type == 'filter' && v.field === element.value;
					});
					if (index > -1) {
						const objCopy = { ...element };
						objCopy.name = objCopy.name.replace('✓', '');
						objCopy.name = objCopy.name.replace(/^\s+/, '');
						return { ...objCopy, selected: true, name: '✓' + objCopy.name };
					} else {
						const objCopy1 = { ...element };
						objCopy1.name = objCopy1.name.replace('✓', '');
						objCopy1.name = objCopy1.name.replace(/^\s+/, '');
						objCopy1.name = '\xA0\xA0\xA0' + objCopy1.name;
						return { ...objCopy1, selected: false, name: objCopy1.name };
					}
				});
				this.items = newArray || [];
			} else {
				this.items = [];
			}
			this.filterItems = this.items.filter(function (v: any, i: number) {
				return v.show === "true";
			});
			setTimeout(() => {
				this.filterDropdown = '';
				this.displaysingular = '';
				if (filter.length > 0) {
					filter.forEach((element: any) => {
						if (element.type == 'filter') {
							var filterItem = this.items.filter(function (v: any, i: number) {
								return element.field === v.value;
							});
							if (filterItem.length > 0) {
								this.filterDropdown = filterItem[0].value;
								this.displaysingular = filterItem[0].displaysingular;
								if (filterItem[0].type == 'category') {
									this.changeFilter({ target: { value: filterItem[0].value } });
									this.showSearchInput = false;
									this.showDateRange = false;
									if (this.filterDropdown == 'casepatientage') {
										this.showDropdown = false;
										this.showRangeSlider = true;
									} else {
										this.showDropdown = true;
										this.showRangeSlider = false;
									}
									this.filterCatDropdown = element.search;
								} else if (filterItem[0].type == 'suggest') {
									this.showSearchInput = true;
									this.showTextInput = false;
									this.showDropdown = false;
									this.showRangeSlider = false;
									this.searchKeyword = element.search;
									this.showDateRange = false;
								} else if (filterItem[0].type == 'daterange') {
									this.showSearchInput = false;
									this.showTextInput = false;
									this.showDropdown = false;
									this.showRangeSlider = false;
									this.searchKeyword = element.search;
									var dateArr = element.search.replace("[", "");
									var dateArr = dateArr.replace("]", "");

									var arr = dateArr.split(' TO ');
									// console.log(arr)
									this.defaultFrom = this.common.formatDate(arr[0]);
									this.defaultTo = this.common.formatDate(arr[1]);
									this.showDateRange = true;
								} else {
									this.showSearchInput = false;
									this.showTextInput = true;
									this.showDropdown = false;
									this.showRangeSlider = false;
									this.searchKeyword = element.search;
									this.showDateRange = false;
								}
							}
						} else {
							if (this.items.length > 0) {
								this.filterDropdown = this.items[0].value
								this.displaysingular = this.items[0].displaysingular
								this.searchKeyword = '';
							}
						}
					});
				} else {
					if (this.items.length > 0) {
						this.filterDropdown = this.items[0].value;
						this.displaysingular = this.items[0].displaysingular;
						this.searchKeyword = '';
					}
				}
			}, 100);
			this.clearFilterClass = '';
		} else {
			this.clearFilterClass = 'disabled';
			this.showSearchInput = false;
			this.showDropdown = false;
			this.showTextInput = true;
			this.showRangeSlider = false;
			this.showDateRange = false;
			this.searchKeyword = '';
			this.items = this.localStorageService.getFilterData() || [];
			if (this.items.constructor === Array) {
				this.filterItems = this.items.filter(function (v: any, i: number) {
					return v.show === "true";
				});
			} else {
				this.filterItems = [];
			}

			if (this.items.length > 0) {
				this.filterDropdown = this.items[0].value;
				this.displaysingular = this.items[0].displaysingular;
				this.searchKeyword = '';
			}
		}
	}

	openAdvancedSearch() {
		const modalRef = this.modalService.open(AdvancedsearchmodalComponent, { ariaLabelledBy: 'modal-basic-title', size: 'xxl', scrollable: true });
		modalRef.result.then((result) => {
			if (result) {
				this.applyFilterSubmit();
				this.assignFiltersContent();
			}
		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}

	openMrnSearch() {
		const modalRef = this.modalService.open(MrnModalComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
		modalRef.result.then((result) => {
			if (result) {
				this.applyFilterSubmit();
				this.assignFiltersContent();
			}
		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}

	openSaveSearch() {
		const modalRef = this.modalService.open(SavesearchmodalComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true });
		modalRef.result.then((result) => {

		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}
	openSavedSearchContent() {
		const modalRef = this.modalService.open(SavedsearchcontentmodalComponent, { ariaLabelledBy: 'modal-basic-title', size: 'xxl', scrollable: true });
		modalRef.result.then((result) => {

		}).catch((error) => {
			if (error != 1) {
				this.toastr.error('', 'Something went wrong.');
			}
		});
	}


	async getFilterMetaData(setFacetStatus: boolean = true) {
		const result = await this.searchService.getAllFilter();
		if (result.status == true) {
			this.localStorageService.setFilterData(result.data);
			this.items = result.data;
			if (setFacetStatus) {
				this.filterService.setFacetFromFilterDataArr(this.items, true);
			}

			if (this.items.length > 0) {
				this.filterDropdown = this.items[0]?.value;
				this.displaysingular = this.items[0]?.displaysingular;

				if (this.items[0]?.type == 'category') {
					this.setCategoryOptions(this.filterDropdown, '', 'onload', []);
				} else if (this.items[0]?.type == 'suggest') {
					this.setSuggestOptions('', 'onload');
				} else if (this.items[0]?.type == 'daterange') {
					this.setDateRangeOptions('', 'onload');
				} else {
					this.setElseConditions('', 'onload');
				}
				this.setPlaceHolder(this.items[0]);
			} else {
				this.setPlaceHolder(null);
			}

			if (this.filter.length > 0) {
				const newArray = this.items.map((e: any, i: number) => {
					var c = this.filter.filter((w: any) => {
						return w.type == 'filter' && w.field == e.value;
					});

					if (c.length > 0) {
						this.filterDropdown = e.value;
						if (e.type == 'category') {
							this.changeFilter({ target: { value: e.value } });
							this.setCategoryOptions(this.filterDropdown, c[0].search, 'filtered', []);
						} else if (e.type == 'suggest') {
							this.setSuggestOptions(c[0].search, 'filtered');
						} else if (e.type == 'daterange') {
							this.setDateRangeOptions(c[0].search, 'filtered');
						} else {
							this.setElseConditions(c[0].search, 'filtered');
						}
						const objCopy = { ...e };
						objCopy.name = objCopy.name.replace('✓', '');
						objCopy.name = objCopy.name.replace(/^\s+/, '');
						return { ...objCopy, selected: true, name: '✓' + objCopy.name };
					} else {
						const objCopy1 = { ...e };
						objCopy1.name = objCopy1.name.replace('✓', '');
						objCopy1.name = objCopy1.name.replace(/^\s+/, '');
						objCopy1.name = '\xA0\xA0\xA0' + objCopy1.name;
						return { ...objCopy1, selected: false, name: objCopy1.name };
					}
				});
				this.items = newArray;
			}
			//show in dropdown when "show" attribute is true
			this.filterItems = this.items.filter(function (v: any, i: number) {
				return v.show === "true";
			});
			this.assignFiltersContent();
		}
	}

	setSuggestOptions(searchKeyword: string, type: string) {
		this.showSearchInput = true;
		this.showDropdown = false;
		this.showTextInput = false;
		this.showRangeSlider = false;
		this.showDateRange = false;

		if (type == 'filtered') {
			this.searchKeyword = searchKeyword;
		}
	}

	setDateRangeOptions(searchKeyword: string, type: string) {
		this.showSearchInput = false;
		this.showDropdown = false;
		this.showTextInput = false;
		this.showRangeSlider = false;
		this.showDateRange = true;

		if (type == 'filtered') {
			this.searchKeyword = searchKeyword;
		}
	}

	setCategoryOptions(filterDropdown: string, searchKeyword: string, type: string, options: any = []) {
		this.showSearchInput = false;
		this.showTextInput = false;
		this.showDateRange = false;
		if (filterDropdown == 'casepatientage') {
			this.showDropdown = false;
			this.showRangeSlider = true;
		} else {
			this.showDropdown = true;
			this.showRangeSlider = false;
		}
		if (type == 'filtered') {
			this.filterCatDropdown = searchKeyword;
		} else if (type == 'changeFilter') {
			this.filterCatDropdown = '';
			this.filterDropdownOptions = options;
		}
	}

	setElseConditions(searchKeyword: string, type: string) {
		this.showSearchInput = false;
		this.showDropdown = false;
		this.showTextInput = true;
		this.showRangeSlider = false;
		this.showDateRange = false;

		if (type == 'filtered') {
			this.searchKeyword = searchKeyword;
		}
	}

	changeFilter(event: any) {
		var result = this.items.filter(function (v: any, i: number) {
			return v.value === event.target.value;
		});
		if (result.length > 0) {
			//Update place holder
			this.setPlaceHolder(result[0]);

			if (result[0]?.type == 'category') {
				this.setCategoryOptions(this.filterDropdown, '', 'changeFilter', result[0].options);
			} else if (result[0]?.type == 'suggest') {
				this.setSuggestOptions('', 'filtered');
			} else if (result[0]?.type == 'daterange') {
				this.setDateRangeOptions('', 'filtered');
			} else {
				this.setElseConditions('', 'filtered');
			}
			this.filter.forEach((element: any) => {
				if (element.type == 'filter' && event.target.value == element.field) {
					var filterItem = this.items.filter(function (v: any, i: number) {
						return element.field === v.value;
					});
					if (filterItem.length > 0) {
						this.filterDropdown = filterItem[0].value;
						this.displaysingular = filterItem[0].displaysingular;
						if (filterItem[0].type == 'category') {
							this.setCategoryOptions(this.filterDropdown, element.search, 'filtered', []);
						} else if (filterItem[0].type == 'suggest') {
							this.setSuggestOptions(element.search, 'filtered');
						} else if (filterItem[0]?.type == 'daterange') {
							this.setDateRangeOptions(element.search, 'filtered');
						} else {
							this.setElseConditions(element.search, 'filtered');
						}
					}
				}
			});
		}
	}

	selectCategoryOption(event: any) {
		this.filterCatDropdown = event.target.value;
		this.callFilterStore(this.filterCatDropdown, this.filterTermData);
	}

	checkAgeValue() {
		this.filterCatDropdown = "[" + this.minValue + " TO " + this.maxValue + "]";
		this.callFilterStore(this.filterCatDropdown, this.filterTermData);
	}

	applyFilter(event: any) {
		var keyword: String = event.target.value;
		keyword = (keyword || '').trim();
		const keywordLength = keyword.length;
		if (keywordLength > 1) {
			this.searchKeyword = keyword;
			this.showAutoSuggest = true;
			//show autosuggest options
			this.store.dispatch(loadAutoSuggest({ keyword: { content: this.searchKeyword, type: this.filterDropdown } }));
		} else if (keywordLength == 0) {
			this.searchKeyword = '';
			this.filterSubject.next();
			this.showAutoSuggest = false;
		}
	}

	applyFilterSubmit() {
		var keyword: String = this.searchKeyword;
		keyword = (keyword || '').trim();
		keyword = keyword.replace('/', '');
		keyword = keyword.replace('/', '');
		const keywordLength = keyword.length;
		if (keywordLength > 1) {
			this.searchKeyword = keyword;
			this.callFilterStore(this.searchKeyword, this.filterTermData);
		} else if (keywordLength == 0) {
			this.searchKeyword = '';
			this.filterService.setFilterForFacetArr({}, true, 'refreshfilter', true);
		}
	}

	callFilterStore(search: any, from: any = this.filterTermData) {
		const data: any = {
			"field": this.filterDropdown,
			"search": search,
			"text": search,
			"category": this.filterDropdown,
			"andcondition": true,
			"type": "filter"
		}
		if ((this.displaysingular || '') != '') {
			data.displaysingular = this.displaysingular;
		}
		this.filterService.setFilterForFacetArr(data, true, from, true);
		//this.store.dispatch(loadFilter({ dataFilter: { content: data, checked: true, from: from } }));
	}

	sortOrder(field: any, title: any) {
		var sortBy = field;
		this.filterService.setSortOrder(sortBy, true);
		//this.store.dispatch(loadSortBy({ sortData: { sortBy: sortBy } }));
		this.sortByText = title;
	}

	clearFilter() {
		localStorage.removeItem('search-url');
		localStorage.removeItem('filter');
		localStorage.removeItem('page');
		localStorage.removeItem('sortBy');
		localStorage.removeItem('adv-filter-data');
		localStorage.removeItem('mrn');
		this.router.navigate([], {
			relativeTo: this.activatedRoute,
			queryParams: {},
			replaceUrl: true
		});
		this.filter = [];
		this.filterCatDropdown = '';
		this.filterDropdown = '';
		this.searchKeyword = '';
		this.getFilterMetaData(false);
		this.minValue = 0;
		this.maxValue = 100;
		// this.defaultFrom = new Date();
		// this.defaultTo = new Date(this.defaultFrom.getTime() + 2 * 24 * 60 * 60 * 1000);

		this.defaultFrom = "";
		this.defaultTo = "";

		this.callFilterStore(this.searchKeyword, this.filterTermClear);

	}

	public onDateRangeSelection(range: { from: Date, to: Date }) {
		var date = new Date(range.from); // M-D-YYYY
		date.setDate(date.getDate() + 2);
		var d = date.getDate();
		var m = date.getMonth() + 1;
		var y = date.getFullYear();

		var dateStringFrom = y + '-' + (m <= 9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d) + 'T00:00:00Z';

		var dateTo = new Date(range.to); // M-D-YYYY
		dateTo.setDate(dateTo.getDate() + 2);
		var dT = dateTo.getDate();
		var mT = dateTo.getMonth() + 1;
		var yT = dateTo.getFullYear();

		var dateStringTo = yT + '-' + (mT <= 9 ? '0' + mT : mT) + '-' + (dT <= 9 ? '0' + dT : dT) + 'T00:00:00Z';
		this.searchKeyword = "[" + dateStringFrom + ' TO ' + dateStringTo + "]";
		this.callFilterStore(this.searchKeyword, this.filterTermData);
	}

	transformFilteredItem(filteredItem: any) {
		if (filteredItem.field == 'collectiondate') {
			var search = filteredItem.search;
			var s = search.replace("[", "");
			var t = s.replace("]", "");
			var arr = t.split(" ");
			var startDate = this.common.formatDateTime(arr[0]);
			var endDate = this.common.formatDateTime(arr[2]);
			return "Collection Date: " + startDate + " TO " + endDate;
		} else if (filteredItem.field == 'casepatientageyears') {
			var search = filteredItem.search;
			var s = search.replace("[", "");
			var t = s.replace("]", "");
			//var arr = t.split(" ");
			return "Age: " + t;
		} else {
			return '';
		}
	}

	ngOnDestroy() {
		this.subscription.unsubscribe();
	}

	removeFilter(filter: any) {
		if (filter?.type == 'advfilter') {
			localStorage.removeItem('adv-filter-data');
			this.filter.splice(this.filter.length - 1, 1);
			this.filterService.setFilterForFacetArr(null, false, 'refreshfilter', true);
			this.assignFiltersContent();
		} else if (filter?.type == 'advmrn') {
			localStorage.removeItem('mrn');
			this.filter.splice(this.filter.length - 1, 1);
			this.filterService.setFilterForFacetArr(null, false, 'refreshfilter', true);
			this.assignFiltersContent();
		}
		else if (filter?.type == undefined) {
			const data = {
				"field": filter.field,
				"search": filter.search,
				"category": filter.category,
				"andcondition": filter.andcondition,
				"type": filter?.type
			}
			this.searchKeyword = '';
			this.showAutoSuggest = false;
			this.filterService.setFilterForFacetArr(data, false, this.filterTermData, true);
			//this.store.dispatch(loadFilter({ dataFilter: { content: data, checked: false, from: this.filterTermData } }));
		} else {
			const data = {
				"field": filter.field,
				"search": filter.search,
				"category": filter.category,
				"andcondition": filter.andcondition
			}
			this.filterService.setFilterForFacetArr(data, false, this.filterTermData, true);
			//this.store.dispatch(loadFilter({ dataFilter: { content: data, checked: false } }));
		}


	}

	windowEvent(event: any) {
		if (event.keyCode === 13) {
			this.applyFilterSubmit();
		}
	}

	setPlaceHolder(input: any) {
		this.placeholder = (input?.placeholder || '') == '' ? "Start typing a search..." : input?.placeholder;
	}
}
