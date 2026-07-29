import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { SearchComponent } from './components/search/search/search.component';
// import { AdvancedComponent } from './components/search/advanced/advanced.component';
import { PreferenceComponent } from './components/User/preference/preference.component';
import { ExtractRequestComponent } from './components/Forms/extract-request/extract-request.component';
import { RequesthistoryComponent } from './components/requesthistory/requesthistory.component';
import { UserComponent } from './components/Admin/user/listuser/user.component';
import { AuthGuard } from './helpers';
import { UserhistoryComponent } from './components/User/userhistory/userhistory.component';
import { EtllogsComponent } from './components/Admin/logs/etllogs.component';
import { GenderComponent } from './components/gender/ListGender/gender.component';
import { CreategenderComponent } from './components/gender/CreateGender/creategender.component';
import { UpdateGenderComponent } from './components/gender/update-gender/update-gender.component';
import { CreateuserComponent } from './components/Admin/user/createuser/createuser.component';
import { UpdateuserComponent } from './components/Admin/user/updateuser/updateuser.component';
import { ListRoleComponent } from './components/role/list-role/list-role.component';
import { CreateRoleComponent } from './components/role/create-role/create-role.component';
import { UpdateRoleComponent } from './components/role/update-role/update-role.component';
import { ListSepcimentTypeComponent } from './components/SpecimenType/list-sepciment-type/list-sepciment-type.component';
import { CreateSpecimenTypeComponent } from './components/SpecimenType/create-specimen-type/create-specimen-type.component';
import { UpdateSpecimenTypeComponent } from './components/SpecimenType/update-specimen-type/update-specimen-type.component';
import { ListSpecimenSourceComponent } from './components/SpecimenSource/list-specimen-source/list-specimen-source.component';
import { CreateSpecimenSourceComponent } from './components/SpecimenSource/create-specimen-source/create-specimen-source.component';
import { UpdateSpecimenSourceComponent } from './components/SpecimenSource/update-specimen-source/update-specimen-source.component';
import { ListSearchRequestStatusComponent } from './components/SearchRequestStatus/list-search-request-status/list-search-request-status.component';
import { CreateSearchRequestStatusComponent } from './components/SearchRequestStatus/create-search-request-status/create-search-request-status.component';
import { UpdateSearchRequestStatusComponent } from './components/SearchRequestStatus/update-search-request-status/update-search-request-status.component';
import { ListRegionComponent } from './components/Region/list-region/list-region.component';
import { CreateRegionComponent } from './components/Region/create-region/create-region.component';
import { UpdateRegionComponent } from './components/Region/update-region/update-region.component';
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
import { DetailComponent } from './components/search/detail/detail.component';
import { PagenotfoundComponent } from './pagenotfound/pagenotfound.component';
import { CohortComponent } from './components/cohort/cohort.component';
import { AireviewsComponent } from './components/aireviews/aireviews.component';
import { SlideRequestFormComponent } from './components/slide-request/slide-request-form/slide-request-form.component';
import { SlideRequestQueueComponent } from './components/slide-request/slide-request-queue/slide-request-queue.component';
import { CytologyEvaluationFormComponent } from './components/cytology-evaluation/cytology-evaluation-form/cytology-evaluation-form.component';
import { CytologyEvaluationCompletedListComponent } from './components/cytology-evaluation/cytology-evaluation-completed-list/cytology-evaluation-completed-list.component';
import { EmailUsersComponent } from './components/Admin/email-users/email-users.component';
const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
  {
    path: 'search', component: SearchComponent, canActivate: [AuthGuard], data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  {
    path: 'search-detail/:id', component: DetailComponent, canActivate: [AuthGuard], data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  // {
  //   path: 'advancedSearch', component: AdvancedComponent, canActivate: [AuthGuard], data: {
  //     role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
  //   }
  // },
  {
    path: 'adminuser', component: UserComponent,
    canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'SECURITYADMIN']
    }
  },
  {
    path: 'create-user', component: CreateuserComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'SECURITYADMIN']
    }
  },
  {
    path: 'edit-user/:id', component: UpdateuserComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'SECURITYADMIN']
    }
  },

  {
    path: 'etl-logs', component: EtllogsComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'email-users', component: EmailUsersComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'ai-reviews', component: AireviewsComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'extractrequest', component: ExtractRequestComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  {
    path: 'slide-request', component: SlideRequestFormComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER', 'SLIDEROOM']
    }
  },
  {
    path: 'slide-request-queue', component: SlideRequestQueueComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'SLIDEROOM']
    }
  },
  {
    path: 'cytology-evaluation', component: CytologyEvaluationFormComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  {
    path: 'cytology-evaluation/completed', component: CytologyEvaluationCompletedListComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  {
    path: 'cytology-evaluation/:id', component: CytologyEvaluationFormComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  {
    path: 'my-requests', component: RequesthistoryComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST']
    }
  },
  {
    path: 'sex', component: GenderComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-gender', component: CreategenderComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-gender/:id', component: UpdateGenderComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  // {path: 'extractreview' , component: ReviewComponent}
  // {path: 'extractreview' , component: AnalystComponent, canActivate: [AuthGuard]},
  { path: 'preference', component: PreferenceComponent, canActivate: [AuthGuard] },
  { path: 'my-history', component: UserhistoryComponent, canActivate: [AuthGuard] },

  {
    path: 'roles', component: ListRoleComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-role', component: CreateRoleComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-role/:id', component: UpdateRoleComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },

  {
    path: 'specimen-types', component: ListSepcimentTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-specimen-type', component: CreateSpecimenTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-specimen-type/:id', component: UpdateSpecimenTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'specimen-sources', component: ListSpecimenSourceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-specimen-source', component: CreateSpecimenSourceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-specimen-source/:id', component: UpdateSpecimenSourceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'search-request-status', component: ListSearchRequestStatusComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-search-request-status', component: CreateSearchRequestStatusComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-search-request-status/:id', component: UpdateSearchRequestStatusComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'regions', component: ListRegionComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-region', component: CreateRegionComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-region/:id', component: UpdateRegionComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'race', component: ListRaceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-race', component: CreateRaceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-race/:id', component: UpdateRaceComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'hospitals', component: ListHospitalComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-hospital', component: CreateHospitalComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-hospital/:id', component: UpdateHospitalComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'ethnicity', component: ListEthnicityComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-ethnicity', component: CreateEthnicityComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-ethnicity/:id', component: UpdateEthnicityComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'comment-types', component: ListCommentTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'create-comment-type', component: CreateCommentTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'edit-comment-type/:id', component: UpdateCommentTypeComponent, canActivate: [AuthGuard],
    data: {
      role: ['ADMIN', 'DEMOADMIN']
    }
  },
  {
    path: 'cohort', component: CohortComponent, canActivate: [AuthGuard], data: {
      role: ['ADMIN', 'DEMOADMIN', 'ANALYST', 'USER']
    }
  },
  //Wild Card Route for 404 request
  {
    path: '**', pathMatch: 'full',
    component: PagenotfoundComponent
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
