// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
    production: false,
    apiBaseUrl: '',
    recordsPerPage: 10,
    debounceTime: 1000,
    filterDataUrl: 'solrtest/filterdata',
    searchUrl: 'solrtest/search',
    facetUrl: 'solrtest/facet',
    lastdataupdatedUrl: 'solrtest/lastdataupdated',
    suggestStaffUrl: 'solrtest/suggeststaff',
    suggestCommentUrl: 'solrtest/suggestcomment',
    suggestCaseUrl: 'solrtest/suggestcase',
    caseinfo: 'solrtest/caseinfo',
    saveaivoteUrl: 'annotation/createfeedback',
    aifeedbackCaseUrl: 'annotation/getfeedback',
    aifeedbackAllUrl: 'annotation/getfeedbackall',
    markreviewedUrl: 'annotation/updatefeedback',
    tagUrl: 'tagcase/tags',
    textCommentsUrl: 'solrtest/casecomment/text',
    epicCommentsUrl: 'solrtest/casecomment/epic',
    coPathCommentsUrl: 'solrtest/casecomment/copath',
    synopticCommentsUrl: 'solrtest/casecomment/synopticreport',
    annotationConfigUrl: 'solrtest/case/annotationconfig',
    errorExceptionMessage: 'Error during data fetch',
    accessExceptionMessage: 'Permission denied for the request',
    slideRequestUrl: 'sliderequest',
  cytologyEvaluationUrl: 'cytologyevaluation',
  userSearchUrl: 'user/search'
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.

/*
TO DO:
    Advanced Search
*/
