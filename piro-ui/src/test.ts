import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { getTestBed, TestBed, TestModuleMetadata } from '@angular/core/testing';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting,
} from '@angular/platform-browser-dynamic/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { StoreModule } from '@ngrx/store';
import { NgxPaginationModule } from 'ngx-pagination';
import { ToastrModule } from 'ngx-toastr';
import { ConfirmDialogService } from './app/services/confirm-dialog.service';
import { PreviousRouteService } from './app/services/previous-route.service';

@NgModule({
  imports: [
    HttpClientTestingModule,
    FormsModule,
    ReactiveFormsModule,
    NoopAnimationsModule,
    RouterTestingModule,
    NgbModule,
    NgxPaginationModule,
    StoreModule.forRoot({}),
    ToastrModule.forRoot(),
  ],
  exports: [FormsModule, ReactiveFormsModule, NgbModule, NgxPaginationModule],
  providers: [ConfirmDialogService, NgbActiveModal, PreviousRouteService],
})
class SharedTestingModule { }

getTestBed().initTestEnvironment(
  [BrowserDynamicTestingModule, SharedTestingModule],
  platformBrowserDynamicTesting(),
  { teardown: { destroyAfterEach: true } }
);

const configureTestingModule = TestBed.configureTestingModule.bind(TestBed);
TestBed.configureTestingModule = (moduleDef: TestModuleMetadata) =>
  configureTestingModule({
    ...moduleDef,
    schemas: [NO_ERRORS_SCHEMA, ...(moduleDef.schemas || [])],
  });