import { Injectable } from '@angular/core';

@Injectable({
	providedIn: 'root'
})
export class LocalStorageService {

	constructor() { }

	getFilterData(): any {
		var item = localStorage.getItem('filter-data') || '{}';
		return JSON.parse(item);
	}

	setFilterData(input: any) {
		localStorage.setItem('filter-data', JSON.stringify(input || {}));
	}

	getAdancedFilterData(): any {
		var item = localStorage.getItem('adv-filter-data') || '{}';
		return JSON.parse(item);
	}

	setAdancedFilterData(input: any) {
		localStorage.setItem('adv-filter-data', JSON.stringify(input || {}));
	}

	getApiToken(): string {
		var item = localStorage.getItem('api-token') || '';
		return item;
	}

	setApiToken(input: any) {
		// console.log(input);
		localStorage.setItem('api-token', input || '');
	}

	getMrn(): string {
		var item = localStorage.getItem('mrn') || '';
		return item;
	}

	setMrn(input: any) {
		localStorage.setItem('mrn', input || '');
	}

	getLastErrorTimestamp(): number {
		var item = localStorage.getItem('lastErrorTimestamp') || '0';
		return parseInt(item);
	}

	setLastErrorTimestamp(input: any) {
		localStorage.setItem('lastErrorTimestamp', (input || '').toString());
	}

	getSearchUrl(): string {
		var item = localStorage.getItem('search-url') || '';
		return item;
	}

	setSearchUrl(input: any) {
		localStorage.setItem('search-url', input || '');
	}


	getSortBy(): string {
		var item = localStorage.getItem('sortBy') || 'accessiondate';
		return item;
	}

	setSortBy(input: any) {
		localStorage.setItem('sortBy', input || '');
	}

	getPage(): Number {
		var item = localStorage.getItem('page') || '1';
		return parseInt(item);
	}

	setPage(input: any) {
		localStorage.setItem('page', input || '');
	}

	getFilter(): any[] {
		var item = localStorage.getItem('filter') || '[]';
		if(Array.isArray(JSON.parse(item))) {
			return JSON.parse(item);
		} else {
			return JSON.parse(JSON.parse(item));
		}
	}

	setFilter(input: any) {
		localStorage.setItem('filter', JSON.stringify(input || '[]'));
	}

	clear() {
		localStorage.clear();
	}

	clearItem(input: any) {
		localStorage.removeItem(input);
	}
}
