import { createAction, props } from '@ngrx/store';

export const loadFacets = createAction(
    '[Request] LoadAllFacets',
    props<{facets: Request[]}>()
);
export const loadResult = createAction(
    '[Request] LoadAllRequests',
    props<{content: Request[]}>()
);

export const loadFilter = createAction(
    '[Request] LoadFilter',
    props<{dataFilter: any}>()
);

export const facetFilter = createAction(
    '[Request] LoadFilter',
    props<{facetFilter: any}>()
);

export const loadAutoSuggest = createAction(
    '[Request] LoadAutoSuggest',
    props<{keyword: any}>()
);
export const loadSortBy = createAction(
    '[Request] LoadSortBy',
    props<{sortData: any}>()
);