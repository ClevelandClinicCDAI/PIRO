import { NgModule, isDevMode } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
//import { QueryBuilderModule } from "angular2-query-builder";
import { QueryBuilderModule } from "./angular2-query-builder/src/lib/angular2-query-builder.module";

//Toastr
import { CommonModule } from '@angular/common';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';

// import { AngularFontAwesomeModule } from 'angular-font-awesome';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './components/home/home.component';
import { ResultComponent } from './components/search/result/result.component';
// import { AdvancedComponent } from './components/search/advanced/advanced.component';
import { FacetComponent } from './components/search/facet/facet.component';
import { FilterComponent } from './components/search/filter/filter.component';
import { SearchComponent } from './components/search/search/search.component';
import { AboutComponent } from './help/about/about.component';
import { HelpComponent } from './help/help/help.component';
import { ContactComponent } from './help/contact/contact.component';
import { ReviewComponent } from './review/review/review.component';
import { PreferenceComponent } from './components/User/preference/preference.component';
import { ExtractRequestComponent } from './components/Forms/extract-request/extract-request.component';
import { AnalystComponent } from './Dashboard/analyst/analyst.component';
import { UserComponent } from './components/Admin/user/listuser/user.component';

import { HeaderComponent } from './components/header/header.component';
import { CommentDisplayDirective } from './directives/comment-display.directive';

import { StoreModule } from '@ngrx/store';
import { facetReducer, resultReducer, dataFilterReducer, facetFilterReducer, keywordReducer, sortReducer } from './store/result.reducer';
import { environment } from 'src/environments/environment.prod';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { AdvancedsearchmodalComponent } from './components/modal/advancedsearchmodal/advancedsearchmodal.component';
import { SavesearchmodalComponent } from './components/modal/savesearchmodal/savesearchmodal.component';
import { SavedsearchcontentmodalComponent } from './components/modal/savedsearchcontentmodal/savedsearchcontentmodal.component';
import { RequesthistoryComponent } from './components/requesthistory/requesthistory.component';
import { EtllogsComponent } from './components/Admin/logs/etllogs.component';
import { UserhistoryComponent } from './components/User/userhistory/userhistory.component';
import { GenderComponent } from './components/gender/ListGender/gender.component';
import { HeaderInterceptor } from './interceptors/header.interceptor';
import { CreategenderComponent } from './components/gender/CreateGender/creategender.component';
import { UpdateRoleComponent } from './components/role/update-role/update-role.component';
import { ListRoleComponent } from './components/role/list-role/list-role.component';
import { CreateRoleComponent } from './components/role/create-role/create-role.component';
import { UpdateGenderComponent } from './components/gender/update-gender/update-gender.component';
import { ListSepcimentTypeComponent } from './components/SpecimenType/list-sepciment-type/list-sepciment-type.component';
import { CreateSpecimenTypeComponent } from './components/SpecimenType/create-specimen-type/create-specimen-type.component';
import { UpdateSpecimenTypeComponent } from './components/SpecimenType/update-specimen-type/update-specimen-type.component';
import { CreateSpecimenSourceComponent } from './components/SpecimenSource/create-specimen-source/create-specimen-source.component';
import { ListSpecimenSourceComponent } from './components/SpecimenSource/list-specimen-source/list-specimen-source.component';
import { UpdateSpecimenSourceComponent } from './components/SpecimenSource/update-specimen-source/update-specimen-source.component';
import { ListSearchRequestStatusComponent } from './components/SearchRequestStatus/list-search-request-status/list-search-request-status.component';
import { CreateSearchRequestStatusComponent } from './components/SearchRequestStatus/create-search-request-status/create-search-request-status.component';
import { UpdateSearchRequestStatusComponent } from './components/SearchRequestStatus/update-search-request-status/update-search-request-status.component';
import { UpdateRegionComponent } from './components/Region/update-region/update-region.component';
import { CreateRegionComponent } from './components/Region/create-region/create-region.component';
import { ListRegionComponent } from './components/Region/list-region/list-region.component';
import { ListRaceComponent } from './components/Race/list-race/list-race.component';
import { CreateRaceComponent } from './components/Race/create-race/create-race.component';
import { UpdateRaceComponent } from './components/Race/update-race/update-race.component';
import { ListHospitalComponent } from './components/Hospital/list-hospital/list-hospital.component';
import { CreateHospitalComponent } from './components/Hospital/create-hospital/create-hospital.component';
import { UpdateHospitalComponent } from './components/Hospital/update-hospital/update-hospital.component';
import { ListEthnicityComponent } from './components/Ethnicity/list-ethnicity/list-ethnicity.component';
import { CreateEthnicityComponent } from './components/Ethnicity/create-ethnicity/create-ethnicity.component';
import { UpdateEthnicityComponent } from './components/Ethnicity/update-ethnicity/update-ethnicity.component';
import { ListCommentTypeComponent } from './components/CommentType/list-comment-type/list-comment-type.component';
import { CreateCommentTypeComponent } from './components/CommentType/create-comment-type/create-comment-type.component';
import { UpdateCommentTypeComponent } from './components/CommentType/update-comment-type/update-comment-type.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { CreateuserComponent } from './components/Admin/user/createuser/createuser.component';
import { ConfirmDialogComponent } from './components/confirm-dialog/confirm-dialog.component';
import { ConfirmDialogService } from './services/confirm-dialog.service';
import { UpdateuserComponent } from './components/Admin/user/updateuser/updateuser.component';
import { ContenttextComponent } from './components/common/contenttext/contenttext.component';
import { AutosuggestComponent } from './components/common/autosuggest/autosuggest.component';
import { ToastComponent } from './components/toast/toast.component';
import { ToasterComponent } from './components/toaster/toaster.component'; 

import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { DetailComponent } from './components/search/detail/detail.component';
import { PreviousRouteService } from './services/previous-route.service';
import { TagComponent } from './components/modal/tag/tag.component';
import { CreatetagComponent } from './components/modal/createtag/createtag.component';
import { TagDisplayDirective } from './directives/tag-display.directive';
import { FacetloaderComponent } from './components/search/facetloader/facetloader.component';
import { DateRangeSelectionComponent } from './components/date-range-selection/date-range-selection.component';
import { CatImageUrlPipe } from './components/common/contenttext/rtfpipe';
import { CommentTextComponent } from './components/common/comment-text/comment-text.component';
import { PagenotfoundComponent } from './pagenotfound/pagenotfound.component';
import { AuditReportComponent } from './components/report/audit-report/audit-report.component';
import { ExportfieldComponent } from './components/modal/exportfield/exportfield.component';
import { ViewsearchComponent } from './components/modal/viewsearch/viewsearch.component';
import { RequestNotesComponent } from './components/modal/request-notes/request-notes.component';
import { SynopticEpicComponent } from './components/common/synoptic-epic/synoptic-epic.component';
import { SynopticCopathComponent } from './components/common/synoptic-copath/synoptic-copath.component';
import { MrnModalComponent } from './components/modal/mrn-modal/mrn-modal.component';
import { CohortComponent } from './components/cohort/cohort.component';
import { AddcohortComponent } from './components/cohort/addcohort/addcohort.component';
import { EditcohortComponent } from './components/cohort/editcohort/editcohort.component';
import { AiVoteComponent } from './components/modal/ai-vote/ai-vote.component';
import { AireviewComponent } from './components/modal/aireview/aireview.component';
import { AireviewsComponent } from './components/aireviews/aireviews.component';
import { AiAuditComponent } from './components/modal/ai-audit/ai-audit.component';
import { AireviewcasedetailComponent } from './components/modal/aireviewcasedetail/aireviewcasedetail.component';
import { UserattestComponent } from './components/modal/userattest/userattest.component';
import { SlideRequestFormComponent } from './components/slide-request/slide-request-form/slide-request-form.component';
import { SlideRequestQueueComponent } from './components/slide-request/slide-request-queue/slide-request-queue.component';
import { EmailUsersComponent } from './components/Admin/email-users/email-users.component';
@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    HomeComponent,
    ResultComponent,
    // AdvancedComponent,
    FacetComponent,
    FilterComponent,
    SearchComponent,
    AboutComponent,
    HelpComponent,
    ContactComponent,
    ReviewComponent,
    PreferenceComponent,
    ExtractRequestComponent,
    AnalystComponent,
    UserComponent,
    HeaderComponent,
    CommentDisplayDirective,
    AdvancedsearchmodalComponent,
    SavesearchmodalComponent,
    SavedsearchcontentmodalComponent,
    RequesthistoryComponent,
    EtllogsComponent,
    UserhistoryComponent,
    GenderComponent,
    CreategenderComponent,
    UpdateRoleComponent,
    ListRoleComponent,
    CreateRoleComponent,
    UpdateGenderComponent,
    ListSepcimentTypeComponent,
    CreateSpecimenTypeComponent,
    UpdateSpecimenTypeComponent,
    CreateSpecimenSourceComponent,
    ListSpecimenSourceComponent,
    UpdateSpecimenSourceComponent,
    ListSearchRequestStatusComponent,
    CreateSearchRequestStatusComponent,
    UpdateSearchRequestStatusComponent,
    UpdateRegionComponent,
    CreateRegionComponent,
    ListRegionComponent,
    ListRaceComponent,
    CreateRaceComponent,
    UpdateRaceComponent,
    ListHospitalComponent,
    CreateHospitalComponent,
    UpdateHospitalComponent,
    ListEthnicityComponent,
    CreateEthnicityComponent,
    UpdateEthnicityComponent,
    ListCommentTypeComponent,
    CreateCommentTypeComponent,
    UpdateCommentTypeComponent,
    CreateuserComponent,
    ConfirmDialogComponent,
    UpdateuserComponent,
    ContenttextComponent,
    AutosuggestComponent,
    ToastComponent,
    ToasterComponent,
    DetailComponent,
    TagComponent,
    CreatetagComponent,
    TagDisplayDirective,
    FacetloaderComponent,
    DateRangeSelectionComponent,
    CatImageUrlPipe,
    CommentTextComponent,
    PagenotfoundComponent,
    AuditReportComponent,
    ExportfieldComponent,
    ViewsearchComponent,
    RequestNotesComponent,
    SynopticEpicComponent,
    SynopticCopathComponent,
    MrnModalComponent,
    CohortComponent,
    AddcohortComponent,
    EditcohortComponent,
    AiVoteComponent,
    AireviewComponent,
    AireviewsComponent,
    AiAuditComponent,
    AireviewcasedetailComponent,
    UserattestComponent,
    SlideRequestFormComponent,
    SlideRequestQueueComponent,
    EmailUsersComponent
  ],
  imports: [
    CommonModule, 
    BrowserAnimationsModule, // required animations module
    ToastrModule.forRoot({
      closeButton:true
    }), // ToastrModule added,
    NgxPaginationModule,
    FormsModule,
    HttpClientModule,
    BrowserModule,
    NgbModule,
    AppRoutingModule,
    QueryBuilderModule,
    ReactiveFormsModule,
    StoreModule.forRoot({ facets: facetReducer,
      content: resultReducer,
      dataFilter:dataFilterReducer,
      facetFilter:facetFilterReducer,
      keyword:keywordReducer,
      sortData:sortReducer }),
    !environment.production ? StoreDevtoolsModule.instrument() : [],
    NgxSliderModule,
    NgxSkeletonLoaderModule
  ],
  providers: [{
    provide: HTTP_INTERCEPTORS,
    useClass: HeaderInterceptor,
    multi: true
  },
  ConfirmDialogService,PreviousRouteService],
  bootstrap: [AppComponent]
})
export class AppModule { }
  
