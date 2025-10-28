import { createReducer, on } from '@ngrx/store';
import { loadResult, loadFacets, loadFilter, loadAutoSuggest, loadSortBy, facetFilter } from './result.actions';

// New Interface for Request State
export interface RequestState {
    facets: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialState: RequestState = {
    facets: []
};

export const facetReducer = createReducer(
  requestInitialState,
  //on(loadResult, (state,{data}) => ({...state,data : data}))
  on(loadFacets, (state , { facets }) => ({
    ...state,
    facets : facets
  }))
);

// New Interface for Request State
export interface RequestContentState {
  content: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialContentState: RequestContentState = {
  content: []
};

export const resultReducer = createReducer(
  requestInitialContentState,
  on(loadResult, (state , { content }) => ({
    ...state,
    content : content
  })),
);

// New Interface for Request State
export interface RequestDataFilterState {
  dataFilter: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialDataFilterState: RequestDataFilterState = {
  dataFilter: []
};

export const dataFilterReducer = createReducer(
  requestInitialDataFilterState,
  on(loadFilter, (state , { dataFilter }) => ({
    ...state,
    dataFilter : dataFilter
  })),
);


// New Interface for Request State
export interface RequestFacetFilterState {
  facetFilter: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialFacetFilterState: RequestFacetFilterState = {
  facetFilter: []
};

export const facetFilterReducer = createReducer(
  requestInitialFacetFilterState,
  on(facetFilter, (state , { facetFilter }) => ({
    ...state,
    facetFilter : facetFilter
  })),
);


// New Interface for Keyword State
export interface RequestKeywordState {
  keyword: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialKeywordState: RequestKeywordState = {
  keyword: []
};

export const keywordReducer = createReducer(
  requestInitialKeywordState,
  on(loadAutoSuggest, (state , { keyword }) => ({
    ...state,
    keyword : keyword
  })),
);


// New Interface for Keyword State
export interface RequestSortState {
  sortData: Request[];
}

// Initialize Store State with Request Initial Const and empty values
export const requestInitialSortState: RequestSortState = {
  sortData: []
};

export const sortReducer = createReducer(
  requestInitialSortState,
  on(loadSortBy, (state , { sortData }) => ({
    ...state,
    sortData : sortData
  })),
);