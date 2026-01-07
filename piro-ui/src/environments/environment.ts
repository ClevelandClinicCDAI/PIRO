// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
    production: false,
    apiBaseUrl: 'http://localhost:8001/',
    recordsPerPage: 10,
    debounceTime: 1000,
    filterDataUrl: 'solr/filterdata',
    searchUrl: 'solr/search',
    facetUrl: 'solr/facet',
    lastdataupdatedUrl: 'solr/lastdataupdated',
    suggestStaffUrl: 'solr/suggeststaff',
    suggestCommentUrl: 'solr/suggestcomment',
    suggestCaseUrl: 'solr/suggestcase',
    caseinfo: 'case/caseinfo',
    saveaivoteUrl: 'annotation/createfeedback',
    aifeedbackCaseUrl: 'annotation/getfeedback',
    aifeedbackAllUrl: 'annotation/getfeedbackall',
    aifeedbackDataUrl: 'annotation/getfeedbackdata',
    aicaseauditlUrl: 'annotation/getaudit',
    isPendingAiFeedbackReviewUrl: 'annotation/ispendingreview',
    markreviewedUrl: 'annotation/updatefeedback',
    tagUrl: 'tagcase/tags',
    textCommentsUrl: 'casecomment/text',
    epicCommentsUrl: 'casecomment/epic',
    coPathCommentsUrl: 'casecomment/copath',
    synopticCommentsUrl: 'casecomment/synopticreport',
    annotationConfigUrl: 'case/annotationconfig',
    getAttestationUrl: "token/attest",
    saveAttestationUrl: "token/saveattest",
    errorExceptionMessage: 'Error during data fetch',
    accessExceptionMessage: 'Permission denied for the request',
    slideRequestUrl: 'sliderequest'
};


export const environment_local = {
    production: false,
    apiBaseUrl: 'http://localhost:8001/',
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
    saveaivoteUrl: 'solrtest/annotation/createfeedback',
    aifeedbackCaseUrl: 'solrtest/annotation/getfeedback',
    aifeedbackAllUrl: 'solrtest/annotation/getfeedbackall',
    aifeedbackDataUrl: 'solrtest/annotation/getfeedbackdata',
    aicaseauditlUrl: 'solrtest/annotation/getaudit',
    isPendingAiFeedbackReviewUrl: 'solrtest/annotation/ispendingreview',
    markreviewedUrl: 'solrtest/annotation/updatefeedback',
    tagUrl: 'tagcase/tags',
    textCommentsUrl: 'solrtest/casecomment/text',
    epicCommentsUrl: 'solrtest/casecomment/epic',
    coPathCommentsUrl: 'solrtest/casecomment/copath',
    synopticCommentsUrl: 'solrtest/casecomment/synopticreport',
    annotationConfigUrl: 'solrtest/case/annotationconfig',
    getAttestationUrl: "token/attest",
    saveAttestationUrl: "token/saveattest",
    errorExceptionMessage: 'Error during data fetch',
    accessExceptionMessage: 'Permission denied for the request',
    slideRequestUrl: 'sliderequest'
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
