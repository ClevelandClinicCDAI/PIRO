import { Component, Input } from '@angular/core';
import { PreviousRouteService } from '../../../services/previous-route.service';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { SearchService } from '../../../services/search.service';
import { LocalStorageService } from '../../../services/localStorage.service';
import { Common } from '../../../helpers';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AiVoteComponent } from '../../modal/ai-vote/ai-vote.component';
import { AireviewComponent } from '../../modal/aireview/aireview.component';
import { AuthService } from '../../../services/auth.service';
import { AiAuditComponent } from '../../modal/ai-audit/ai-audit.component';
@Component({
	selector: 'app-detail',
	templateUrl: './detail.component.html',
	styleUrls: ['./detail.component.css']
})
export class DetailComponent {

	@Input() public caseIdInput: number = 0;

	prevUrl = '';
	currUrl = '';
	item: any;
	caseid: any;
	textComments: any = [];
	epicComments: any = [];
	coPathComments: any = [];
	coPathSynopticComments: any = [];
	showEpic: boolean = false;
	showCopath: boolean = false;
	showMigrated: boolean = false;
	showSynoptic: boolean = false;
	showAI: boolean = false;
	classEpic: string = "";
	classCopath: string = "";
	classMigrated: string = "";
	classCase: string = "";
	classAI: string = "";
	caseSource: string = "";
	specimensGroup: any = [];
	specimens: any = [];
	versionDate: any = null;
	synopticComments: any = [];
	synopticReports: any = [];
	patientComments: any = [];
	caseAttrExclude: any = [];

	isAge: boolean = false;
	isName: boolean = false;
	isGender: boolean = false;
	role: string = '';
	isReviewAnnotation: boolean = false;

	synopticlistId: string = '';
	synopticlist: any = [];
	annotationConfig: any = [];
	contentLoaded = false;
	contentText: string = "";

	isShowBreadcrumb: boolean = true;

	constructor(private authService: AuthService,
		private previousRouteService: PreviousRouteService,
		private router: Router,
		private searchService: SearchService,
		private activatedRoute: ActivatedRoute,
		private common: Common,
		private localStorageService: LocalStorageService,
		private modalService: NgbModal) { }

	async ngOnInit() {

		this.contentLoaded = false;
		this.prevUrl = this.previousRouteService.getPreviousUrl();
		this.currUrl = this.previousRouteService.getCurrentUrl();
		if(this.caseIdInput == 0) {
			this.caseid = this.activatedRoute.snapshot.paramMap.get('id');
			this.isShowBreadcrumb = true;
		} else {
			this.caseid = this.caseIdInput;
			this.isShowBreadcrumb = false;
		}
		// console.log("caseIdInput ", this.caseid)
		var auth: any = await this.authService.getIsAuth();
		this.role = auth?.role;
		this.isReviewAnnotation = ['ADMIN', 'DEMOADMIN'].includes(this.role);
		this.loadConfig();
		this.getDetail();
		this.contentLoaded = true;
	}

	async loadConfig() {
		const result = await this.searchService.getAnnotationConfig();
		if (result.status == true) {
			this.annotationConfig = result.data;
			for (let item of this.annotationConfig) {
				const resultVote = await this.searchService.getFeedbackData(this.caseid, item.annotationConfigurationId);
				if (resultVote.status == true) {
					// console.log("resultVote: ", resultVote);
					item.postiveVoteCount = resultVote.data?.postiveVoteCount;
					item.negativeVoteCount = resultVote.data?.negativeVoteCount;
					item.myVote = resultVote.data?.myVote;
				}
			}
		}
		// console.log("annotationConfig: ", this.annotationConfig);
	}

	async getDetail() {
		const result = await this.searchService.getCaseDetail(this.caseid);
		if (result.status == true) {
			this.item = result.data;
			this.caseAttrExclude = this.item.attrExcludes;
			this.isAge = this.showAttr('CasePatientAgeYears');
			this.isName = this.showAttr('PatientName');
			this.isGender = this.showAttr('PatientGender');


			if (this.item?.case?.isepic) {
				this.showEpic = true;
				//this.classEpic = "active";
			}
			if (this.item?.case?.iscopath) {
				this.showCopath = true;
			}
			if (this.item?.case?.ismigrated) {
				this.showMigrated = true;
			}
			// if (this.item?.case?.annotationmalignant != '-') {
			// 	this.showAI = true;
			// }
			// this.showAI = true;
			// this.classAI = "show active";

			if (this.item?.specimensGroup.length > 0) {
				this.showSynoptic = true;
				this.specimensGroup = this.item?.specimensGroup;
				this.specimens = this.item?.specimens;
				this.specimensGroup.forEach((item: any) => {
					item.specimens = item.specimenGrp.split(',');
					item.ids = item.synopticId.split(',');
				});
				this.synopticlistId = this.specimensGroup.length > 0 ? this.specimensGroup[0].synopticId : '-';
				// console.log(this.specimensGroup);
				// console.log(this.synopticlistId);
			}

			if (!this.isShowBreadcrumb || this.caseIdInput != 0) {
				this.classAI = "show active";
			}
			else if (this.item?.case?.iscopath) {
				if(this.isShowBreadcrumb) {
					this.classCopath = "show active";
				}
				
				this.getCoPathComments();
				this.caseSource = "CoPath";
			}
			else if (this.item?.case?.isepic) {
				if(this.isShowBreadcrumb) {
					this.classEpic = "show active";
				}
				
				this.getEpicComments();
				this.caseSource = "Epic";
			}			
			else if (this.item?.case?.ismigrated) {
				if(this.isShowBreadcrumb) {
					this.classMigrated = "show active";
				}
				
				this.getTextComments();
				this.caseSource = "Unknown";
			} else {
				if(this.isShowBreadcrumb) {
					this.classCase = "show active";
				}
			}
		}
	};

	showAttr(attr: string): boolean {
		var data = this.caseAttrExclude.filter((item: any) => item === attr);
		return data.length == 0;
	}

	back() {
		var searchUrlFrom: string = this.localStorageService.getSearchUrl();
		if (searchUrlFrom == '') {
			this.router.navigate(['/search']);
		} else {
			let params = searchUrlFrom.split('&page=');
			if (params.length > 0) {
				var searchFilter = params[0].replace('searchFilter=', '');
			} else {
				var searchFilter = '{}';
			}
			const arrSearchFilter = JSON.parse(searchFilter);
			if (!Array.isArray(arrSearchFilter)) {
				this.router.navigate(['/search']);
			} else {
				var pagesortby = params[1].split('&sortBy=');
				var page = pagesortby[0];
				var sortBy = pagesortby[1];
				this.router.navigate(['/search'], {
					queryParams: { searchFilter: JSON.stringify(arrSearchFilter), page: page, sortBy: sortBy },
					replaceUrl: true
				});
			}
		}
	}
	convertData(attr: string, data: any) {
		if (this.showAttr(attr)) {
			return data;
		} else {
			return "******";
		}
	}

	convertAnnotationData(attr: string, data: any) {
		if (this.showAttr(attr)) {
			return data;
		} else {
			return "-";
		}
	}

	convertDate(attr: string, date: any) {
		if (this.showAttr(attr)) {
			return (date == null || date === '' || date === 'None') ? "" : this.common.formatDateTime(date);
		} else {
			return "**/**/****";
		}
	}

	async getTextComments() {
		this.contentLoaded = false;
		const result = await this.searchService.getTextComments(this.caseid);
		if (result.status == true) {
			this.textComments = result.data;
		}
		this.contentLoaded = true;
	}
	async getEpicComments() {
		this.contentLoaded = false;
		const result = await this.searchService.getEpicComments(this.caseid);
		if (result.status == true) {
			this.epicComments = result.data;
		}
		this.contentLoaded = true;
	}
	async getCoPathComments() {
		this.contentLoaded = false;
		const result = await this.searchService.getCoPathComments(this.caseid);
		if (result.status == true) {
			this.coPathComments = result.data;
			this.coPathSynopticComments = this.coPathComments.filter((item: any) => item.type == 'Synoptic');
		}
		this.contentLoaded = true;
	}






	async getSynopticComments() {
		this.getSynopticText(this.synopticlistId);
	}

	async onSynopticChange(event: any) {
		this.getSynopticTextForId(event.target.value);
	}

	async buildSynopticDataSource(synopticlistId: any) {
		var that = this;
		that.synopticlist = [];
		var synopticlistIds = synopticlistId.split(',');
		synopticlistIds.forEach((currentValue: any, index: number) => {
			that.synopticlist.push({ text: 'Version ' + (synopticlistIds.length - index), id: currentValue });
		});
		// console.log(that.synopticlist);
	}

	async getSynopticText(synopticlistId: any) {
		this.contentLoaded = false;
		this.synopticlistId = synopticlistId;
		this.buildSynopticDataSource(synopticlistId);
		this.getSynopticTextForId(synopticlistId.split(',')[0]);
	}

	async getSynopticTextForId(synopticId: any) {
		// console.log(event);
		this.contentLoaded = false;

		var synData = this.specimens.filter((p: any) => p.synopticId == synopticId);
		// console.log(synData);
		if (synData.length > 0) {
			this.versionDate = synData[0].recordDate;
		}
		const result = await this.searchService.getSynopticComments(synopticId);
		if (result.status == true) {
			this.patientComments = result.data?.patient;
			this.synopticComments = result.data?.synoptic;
			this.synopticReports = result.data?.report;
		}
		this.contentLoaded = true;
	}


	openAiVote(annotationConfigurationId: number, caseid: number, vote: number, annotationName: string) {
		const modalRef = this.modalService.open(AiVoteComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true, backdrop: 'static', keyboard: false });
		modalRef.componentInstance.caseid = caseid;
		modalRef.componentInstance.casenum = this.item?.case?.casenumber;
		modalRef.componentInstance.vote = vote;
		modalRef.componentInstance.annotationConfigurationId = annotationConfigurationId;
		modalRef.componentInstance.annotationName = annotationName;
		modalRef.result.then((result) => {
			this.loadConfig();
		}).catch((error) => {

		});
	}

	openAiReview(annotationConfigurationId: number, caseid: number, annotationName: string) {
		const modalRef = this.modalService.open(AireviewComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true, backdrop: 'static', keyboard: false });
		modalRef.componentInstance.caseid = caseid;
		modalRef.componentInstance.casenum = this.item?.case?.casenumber;
		modalRef.componentInstance.annotationConfigurationId = annotationConfigurationId;
		modalRef.componentInstance.annotationName = annotationName;
		modalRef.result.then((result) => {

		}).catch((error) => {

		});
	}

	openAiAudit(annotationConfigurationId: number, caseid: number, annotationName: string) {
		const modalRef = this.modalService.open(AiAuditComponent, { ariaLabelledBy: 'modal-basic-title', size: 'lg', scrollable: true, backdrop: 'static', keyboard: false });
		modalRef.componentInstance.caseid = caseid;
		modalRef.componentInstance.casenum = this.item?.case?.casenumber;
		modalRef.componentInstance.annotationConfigurationId = annotationConfigurationId;
		modalRef.componentInstance.annotationName = annotationName;
		modalRef.result.then((result) => {

		}).catch((error) => {

		});
	}
}
