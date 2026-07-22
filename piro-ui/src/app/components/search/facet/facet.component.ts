import { Component, HostListener } from '@angular/core';
import { Store } from '@ngrx/store';
import { BehaviorSubject, Observable, Subscription, take } from 'rxjs';
import { SearchService } from '../../../services/search.service';
import { FilterService } from '../../../services/filter.service';
import { loadFilter } from '../../../store/result.actions';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { LocalStorageService } from '../../../services/localStorage.service';
import { Options } from "@angular-slider/ngx-slider";
import { PatientService } from '../../../services/patient.service';
import { CohortService } from '../../../services/cohort.service';

@Component({
  standalone: false,
	selector: 'app-facet',
	templateUrl: './facet.component.html',
	styleUrls: ['./facet.component.css']
})
export class FacetComponent {
	private readonly regionFacetLabels: Record<string, string> = {
		Florida: 'Weston',
		Ohio: 'Ohio (other)'
	};

	minValue: number = 0;
	maxValue: number = 100;

	deceased: string = 'NA';
	concentriq: string = 'NA';
	options: Options = {
		floor: 0,
		ceil: 100
	};
	facets!: Observable<any>;
	malignants: any;
	cohorts: any;
	genders: any;
	regions: any;
	casetype: any;
	consultationtype: any;
	specialtytype: any;
	malignantFilter: any = [];
	gendersFilter: any = [];
	cohortsFilter: any = [];
	regionsFilter: any = [];
	caseTypeFilter: any = [];
	consultationTypeFilter: any = [];
	specialtyTypeFilter: any = [];
	casePatientAgeFilter = [];
	filterTotal: number = 0;
	filterTotalConcentriq: number = 0;
	filter: any = [];
	contentLoaded = true;
	screenWidth: any;
	dataFilterSubscription!: Subscription;
	facetFilterSubscription!: Subscription;
	mrn: string = '';
	mrnDisplay: string = '';
	defaultSortBy: any = 'accessiondate';
	patientLimit: number = 1;

	private facetFromFilterDataSubscription: Subscription = new Subscription();
	private filterForFacetSubscription: Subscription = new Subscription();

	constructor(
		private searchService: SearchService,
		private filterService: FilterService,
		private patientService: PatientService,
		private cohortService: CohortService,
		private localStorageService: LocalStorageService) {
	}

	async ngOnInit() {
		const result = await this.cohortService.getCohortFacet();
		if (result.status == true) {			 
			this.cohortsFilter = result.data;
		}

		this.facetFromFilterDataSubscription = this.filterService.getFacetFromFilterDataArr().subscribe((data: any) => {
			if (data.status) {
				if (data.facets.length > 0) {
					this.gendersFilter = this.getFiltersOptions(data.facets, 'gender');
					this.malignantFilter = this.getFiltersOptions(data.facets, 'annotationmalignant');
					// this.cohortsFilter = this.getFiltersOptions(data.facets, 'cohort');
					this.regionsFilter = this.getFiltersOptions(data.facets, 'region');
					this.caseTypeFilter = this.getFiltersOptions(data.facets, 'casetypecategory');
					this.consultationTypeFilter = this.getFiltersOptions(data.facets, 'reviewtype');
					this.casePatientAgeFilter = this.getFiltersOptions(data.facets, 'casepatientage');
					this.specialtyTypeFilter = this.getFiltersOptions(data.facets, 'specialty');

					this.filter = [];
					this.minValue = 0;
					this.maxValue = 100;
					this.deceased = "NA";
					this.concentriq = "NA";
					this.getAllFacets();
				}
			}
		});
		this.filterForFacetSubscription = this.filterService.getFilterForFacetArr().subscribe((data: any) => {
			if (data.status) {
				this.filter = data.filters;
				this.localStorageService.setFilter(this.filter)
				this.localStorageService.setPage(data.page)
				this.localStorageService.setSortBy(data.sortBy)
				// localStorage.setItem('filter',JSON.stringify(this.filter));
				// localStorage.setItem('page', data.page.toString());
				// localStorage.setItem('sortBy', data.sortBy != '' ? data.sortBy : this.defaultSortBy);
				this.getAllFacets();
				if (this.filter.length > 0) {
					var c = this.filter.filter((w: any) => {
						return w.field == "casepatientageyears" && w?.type != 'filter';
					});
					if (c.length > 0) {
						var search = c[0].search.replace("[", '');
						var search = search.replace("]", "");
						var search = search.split(" TO ");
						this.minValue = search[0];
						this.maxValue = (search[1] == '*') ? 100 : search[1];
					} else {
						this.minValue = 0;
						this.maxValue = 100;
					}

					c = this.filter.filter((w: any) => {
						return w.field == "isdeceased";
					});
					if (c.length > 0) {
						this.deceased = c[0].search;
					} else {
						this.deceased = "NA";
					}



					c = this.filter.filter((w: any) => {
						return w.field == "isconcentriq";
					});
					if (c.length > 0) {
						this.concentriq = c[0].search;
					} else {
						this.concentriq = "NA";
					}
				}
				//call Result
				this.filterService.setResultPayload(data.filters, data.page, data.sortBy, data.type, true);
			}
		});
	}

	ngOnDestroy() {
		this.filterService.setFacetFromFilterDataArr([], false);
		this.facetFromFilterDataSubscription.unsubscribe();

		this.filterService.setFilterForFacetArr({}, true, '', false);

		this.filterForFacetSubscription.unsubscribe();
	}

	ngAfterViewInit(): void {
		this.screenWidth = window.innerWidth;
		this.updateAccordian(this.screenWidth);
	}

	@HostListener('window:resize', ['$event'])
	onResize(event: any) {
		this.screenWidth = window.innerWidth;
		this.updateAccordian(this.screenWidth);
	}

	updateAccordian(screenWidth: number) {
		if (screenWidth < 768) {
			const buttons = document.querySelectorAll('.accordion-button');
			for (const button of buttons) {
				button.classList.add('collapsed');
			}
			const accordions = document.querySelectorAll('.accordion-collapse');
			for (const acc of accordions) {
				acc.classList.remove('show');
			}
		} else {
			const buttons = document.querySelectorAll('.accordion-button');
			for (const button of buttons) {
				button.classList.remove('collapsed');
			}
			const accordions = document.querySelectorAll('.accordion-collapse');
			for (const acc of accordions) {
				acc.classList.add('show');
			}
		}
	}

	getFiltersOptions(facets: any, type: any) {
		var arr = facets.filter(function (v: any, i: number) {
			return v.value === type;
		});
		return arr[0]?.options || [];
	}

	async getAllFacets() {

		// var filterArr = JSON.parse(localStorage.getItem('filter') || '[]');
		var filterArr = this.localStorageService.getFilter();
		this.contentLoaded = false;
		var advFilter = this.localStorageService.getAdancedFilterData();
		this.mrn = this.localStorageService.getMrn();
		if (this.mrn != '') {
			const result = await this.patientService.searchMrn(this.mrn);
			if (result.status == true) {
				if (result.data.length > 0) {
					 this.mrnDisplay = `${result.data[0].firstname} ${result.data[0].lastname} (${this.mrn})`;
				}
			}
		}

		var cohortIds : [] = this.cohortsFilter.map((item: any) => {return item.value});
		// console.log(cohortIds);
		const result = await this.searchService.getAllFacets(filterArr, advFilter, this.mrn, cohortIds);
		if (result.status == true) {
			this.contentLoaded = true;
			this.facets = result.data;
			if (Object.keys(result.data).length > 0) {
				this.genders = result.data?.gender?.facets || [];
				this.malignants = result.data?.annotationmalignant?.facets || [];
				this.cohorts = result.data?.cohorts || [];
				this.regions = result.data?.region?.facets || [];
				this.casetype = result.data?.casetypecategory?.facets || [];
				this.consultationtype = result.data?.reviewtype?.facets || [];
				this.specialtytype = result.data?.specialty?.facets || [];

				var mrns = result.data?.mrn?.facets || [];
				if(mrns.length > 0 && mrns.length <= this.patientLimit)
				{
					this.mrn = mrns[0].key
				}
				var patientnames = result.data?.patientname?.facets || [];
				if(patientnames.length > 0 && patientnames.length <= this.patientLimit)
				{
					this.mrnDisplay = patientnames[0].key
				}

				//genders
				this.genders = this.assignFacetsData(this.gendersFilter, this.genders, 'gender', filterArr);
				//cohorts
				// console.log(this.cohortsFilter);
				// console.log(this.cohorts);
				this.cohorts = this.assignFacetsData(this.cohortsFilter, this.cohorts, 'cohort', filterArr);
				// console.log(this.cohorts);
				//malignant
				this.malignants = this.assignFacetsData(this.malignantFilter, this.malignants, 'annotationmalignant', filterArr);
				// console.log("this.malignants: ", this.malignants);
				//regions
				this.regions = this.assignFacetsData(this.regionsFilter, this.regions, 'region', filterArr);
				//case category
				this.casetype = this.assignFacetsData(this.caseTypeFilter, this.casetype, 'casetypecategory', filterArr);
				//Review type
				this.consultationtype = this.assignFacetsData(this.consultationTypeFilter, this.consultationtype, 'reviewtype', filterArr);
				//Specialty type
				this.specialtytype = this.assignFacetsData(this.specialtyTypeFilter, this.specialtytype, 'specialty', filterArr);
				if (filterArr.length > 0) {
					var c = filterArr.filter((w: any) => {
						return w.field == 'casepatientageyears' && w?.type != 'filter';
					});
					if (c.length > 0) {
						var search = c[0].search.replace("[", '');
						var search = search.replace("]", "");
						var search = search.split(" TO ");
						this.minValue = search[0];
						this.maxValue = (search[1] == '*') ? 100 : search[1];
					}

					c = filterArr.filter((w: any) => {
						return w.field == 'isdeceased';
					});
					if (c.length > 0) {
						this.deceased = c[0].search;
					} else {
						this.deceased = "NA";
					}


					c = filterArr.filter((w: any) => {
						return w.field == 'isconcentriq';
					});
					if (c.length > 0) {
						this.concentriq = c[0].search;
					} else {
						this.concentriq	 = "NA";
					}
				} else {
					this.deceased = "NA";
					this.concentriq = "NA";
					this.minValue = 0;
					this.maxValue = 100;
				}
				this.filterTotal = result.data?.filterTotal || 0;
				this.filterTotalConcentriq = result.data?.filterTotal || 0;
			}
		} else {
			this.contentLoaded = true;
		}
	}

	assignFacetsData(dataFilter: any, data: any, type: any, localStorageData: any) {
		var arr: any = [];
		dataFilter.forEach((element: any) => {
			var r = data.filter((v: any) => {
				var eleVal = (element.value || '').toString();
				return v.key.toLowerCase() == eleVal.toLowerCase();
			});
			if (r.length > 0) {
				arr.push({ key: r[0].key, val: r[0].val, name: element.name, value: element.value, checked: false });
			} else {
				arr.push({ key: element.value, val: 0, name: element.name, value: element.value, checked: false });
			}
		});
		arr.forEach((e: any, i: number) => {
			if (localStorageData.length > 0) {
				var c = localStorageData.filter((w: any) => {
					return w.field == type && w.search == e.key && w?.type != 'filter';
				});
				if (c.length > 0) {
					arr[i].checked = true;
				} else {
					arr[i].checked = false;
				}
			}
		});
		return arr;
	}

	getRegionFacetLabel(regionKey: string) {
		return this.regionFacetLabels[regionKey] || regionKey;
	}

	//Events to track the facet changes and update the data strore
	checkMalignantValue(event: any) {
		this.callLoadFilterStore("annotationmalignant", event.target.value, "annotationmalignant", event.target.checked, event.target.value);
	}

	checkCohortValue(event: any) {
		this.callLoadFilterStore("cohort", event.target.value, "cohort", event.target.checked, event.target.title);
	}

	checkGenderValue(event: any) {
		this.callLoadFilterStore("gender", event.target.value, "gender", event.target.checked, event.target.value);
	}

	checkRegionValue(event: any) {
		this.callLoadFilterStore("region", event.target.value, "region", event.target.checked, event.target.value);
	}

	checkCaseTypeValue(event: any) {
		this.callLoadFilterStore("casetypecategory", event.target.value, "casetypecategory", event.target.checked, event.target.value);
	}

	checkMrnValue(event: any) {
		this.localStorageService.clearItem("mrn");
		this.mrn = '';
		this.callLoadFilterStore("mrn", event.target.value, "mrn", event.target.checked, event.target.value);
		this.filterService.setFilterForFacetMrnArr();
	}

	checkConsultationTypeValue(event: any) {
		this.callLoadFilterStore("reviewtype", event.target.value, "reviewtype", event.target.checked, event.target.value);
	}

	checkSpecilatyTypeValue(event: any) {
		this.callLoadFilterStore("specialty", event.target.value, "specialty", event.target.checked, event.target.value);
	}

	checkAgeValue() {
		var maxLimit = "";
		if (this.maxValue === 100) {
			maxLimit = "*";
		} else {
			maxLimit = this.maxValue.toString();
		}
		let search = "[" + this.minValue + " TO " + maxLimit + "]";
		this.callLoadFilterStore("casepatientageyears", search, "casepatientageyears", true, search);
	}

	onDeceasedChange(deceased: string) {
		this.deceased = deceased;
		this.callLoadFilterStore("isdeceased", this.deceased, "isdeceased", true, this.deceased);

	};

	onConcentriqChange(concentriq: string) {
		this.concentriq = concentriq;
		this.callLoadFilterStore("isconcentriq", this.concentriq, "isconcentriq", true, this.concentriq);

	};

	callLoadFilterStore(field: any, search: any, category: any, checkedStatus: any, text: any) {
		const data = {
			"field": field,
			"search": search,
			"category": category,
			"andcondition": false,
			"text": text
		}
		if (category == 'casepatientage') {
			this.filterService.setFilterForFacetArr(data, true, 'filter', true);
		} else if (category == 'isdeceased') {
			this.filterService.setFilterForFacetArr(data, true, 'filter', true);
		} else if (category == 'isconcentriq') {
			this.filterService.setFilterForFacetArr(data, true, 'filter', true);
		} else if (category == 'mrn1') {
			this.filterService.setFilterForFacetArr(null, false, 'refreshfilter', true);
		} else {
			if (checkedStatus) {
				this.filterService.setFilterForFacetArr(data, true, 'filter', true);
			} else {
				this.filterService.setFilterForFacetArr(data, false, 'filter', true);
			}
		}
	}
}
