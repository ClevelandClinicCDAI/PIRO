import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import {
  CytologyEvaluation,
  CytologyEvaluationSavePayload,
  CytologyEvaluationSiteInput,
  CytologyTerminology,
  UserSearchResult
} from 'src/app/models/cytology-evaluation';
import { CytologyEvaluationService } from 'src/app/services/cytology-evaluation.service';
import { ConfirmDialogService } from 'src/app/services/confirm-dialog.service';
import { ToastService } from 'src/app/services/toast.service';

@Component({
  standalone: false,
  selector: 'app-cytology-evaluation-form',
  templateUrl: './cytology-evaluation-form.component.html',
  styleUrls: ['./cytology-evaluation-form.component.css']
})
export class CytologyEvaluationFormComponent implements OnInit {
  form!: FormGroup;
  terminology: CytologyTerminology = {
    procedureType: [],
    readLocation: [],
    procedureLocation: [],
    site: [],
    adequacy: []
  };

  evaluation: CytologyEvaluation | null = null;
  myEvaluations: CytologyEvaluation[] = [];
  loading = false;
  saving = false;
  prelimVerifying = false;
  finalVerifying = false;
  deleting = false;
  errorMessage = '';
  readonlyMode = false;
  private wasNewOnLastSave = false;

  totals = {
    totalDQ: 0,
    totalPap: 0,
    totalThinPrep: 0,
    totalCellBlock: 0,
    totalUnstainedSlides: 0
  };

  private valueChangesSub: Subscription | null = null;

  constructor(
    private formBuilder: FormBuilder,
    private cytologyEvaluationService: CytologyEvaluationService,
    private toastService: ToastService,
    private confirmDialogService: ConfirmDialogService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  async ngOnInit() {
    this.buildForm();
    this.readonlyMode = this.route.snapshot.queryParamMap.get('readonly') === 'true';

    await this.loadTerminology();
    if (!this.readonlyMode) {
      await this.loadMyEvaluations();
    }

    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      await this.loadEvaluation(Number(idParam));
    }

    if (this.readonlyMode) {
      this.form.disable({ emitEvent: false });
    }

    this.subscribeToValueChanges();
  }

  private subscribeToValueChanges() {
    this.valueChangesSub?.unsubscribe();
    this.valueChangesSub = this.form.valueChanges.subscribe(() => this.recalculateTotals());
  }

  get sites(): FormArray {
    return this.form.get('sites') as FormArray;
  }

  buildForm() {
    this.form = this.formBuilder.group({
      patientIdentifiers: ['', [Validators.maxLength(500)]],
      procedureType: [''],
      procedurePerformedBy: [''],
      evaluationPerformedBy: [''],
      viaTelecytology: [false],
      readLocation: [''],
      procedureLocation: [''],
      assignedToUserId: [null],
      clinicalHistory: ['', [Validators.maxLength(2000)]],
      notes: ['', [Validators.maxLength(2000)]],
      patientHistory: [''],
      cytologyPersonnelUserId: [null],
      pathologistUserId: [null],
      fellowUserId: [null],
      residentUserId: [null],
      totalTimeSpentMinutes: [null, [Validators.min(0)]],
      sites: this.formBuilder.array([this.buildSiteGroup()])
    });
  }

  buildSiteGroup(site?: CytologyEvaluationSiteInput): FormGroup {
    return this.formBuilder.group({
      id: [site?.id ?? null],
      site: [site?.site ?? ''],
      evalEpisodeNumber: [site?.evalEpisodeNumber ?? null, [Validators.min(0)]],
      adequacy: [site?.adequacy ?? ''],
      dqCount: [site?.dqCount ?? 0, [Validators.required, Validators.min(0)]],
      papCount: [site?.papCount ?? 0, [Validators.required, Validators.min(0)]],
      thinPrepCount: [site?.thinPrepCount ?? 0, [Validators.required, Validators.min(0)]],
      cellBlockCount: [site?.cellBlockCount ?? 0, [Validators.required, Validators.min(0)]],
      unstainedSlidesCount: [site?.unstainedSlidesCount ?? 0, [Validators.required, Validators.min(0)]]
    });
  }

  addSite() {
    this.sites.push(this.buildSiteGroup());
    this.recalculateTotals();
  }

  removeSite(index: number) {
    if (this.sites.length <= 1) {
      this.sites.at(0).reset({
        id: null,
        site: '',
        evalEpisodeNumber: null,
        adequacy: '',
        dqCount: 0,
        papCount: 0,
        thinPrepCount: 0,
        cellBlockCount: 0,
        unstainedSlidesCount: 0
      });
    } else {
      this.sites.removeAt(index);
    }
    this.recalculateTotals();
  }

  recalculateTotals() {
    const values = this.sites.value as CytologyEvaluationSiteInput[];
    this.totals = {
      totalDQ: values.reduce((sum, item) => sum + (Number(item.dqCount) || 0), 0),
      totalPap: values.reduce((sum, item) => sum + (Number(item.papCount) || 0), 0),
      totalThinPrep: values.reduce((sum, item) => sum + (Number(item.thinPrepCount) || 0), 0),
      totalCellBlock: values.reduce((sum, item) => sum + (Number(item.cellBlockCount) || 0), 0),
      totalUnstainedSlides: values.reduce((sum, item) => sum + (Number(item.unstainedSlidesCount) || 0), 0)
    };
  }

  async loadTerminology() {
    const result: any = await this.cytologyEvaluationService.getTerminology();
    if (result?.status) {
      this.terminology = result.data;
    } else {
      this.errorMessage = 'Unable to load terminology lists.';
    }
  }

  async loadMyEvaluations() {
    const result: any = await this.cytologyEvaluationService.list();
    if (result?.status) {
      this.myEvaluations = result.data || [];
    }
  }

  async loadEvaluation(id: number) {
    this.loading = true;
    const result: any = await this.cytologyEvaluationService.get(id);
    this.loading = false;
    if (result?.status) {
      this.applyEvaluation(result.data);
    } else {
      this.errorMessage = 'Unable to load the requested evaluation.';
    }
  }

  applyEvaluation(evaluation: CytologyEvaluation) {
    this.evaluation = evaluation;
    this.form.patchValue(
      {
        patientIdentifiers: evaluation.patientIdentifiers,
        procedureType: evaluation.procedureType,
        procedurePerformedBy: evaluation.procedurePerformedBy,
        evaluationPerformedBy: evaluation.evaluationPerformedBy,
        viaTelecytology: !!evaluation.viaTelecytology,
        readLocation: evaluation.readLocation,
        procedureLocation: evaluation.procedureLocation,
        assignedToUserId: evaluation.assignedToUserId,
        clinicalHistory: evaluation.clinicalHistory,
        notes: evaluation.notes,
        patientHistory: evaluation.patientHistory,
        cytologyPersonnelUserId: evaluation.cytologyPersonnelUserId,
        pathologistUserId: evaluation.pathologistUserId,
        fellowUserId: evaluation.fellowUserId,
        residentUserId: evaluation.residentUserId,
        totalTimeSpentMinutes: evaluation.totalTimeSpentMinutes
      },
      { emitEvent: false }
    );

    this.sites.clear();
    const sites = evaluation.sites?.length ? evaluation.sites : [undefined];
    sites.forEach((site) => this.sites.push(this.buildSiteGroup(site)));
    this.recalculateTotals();

    this.router.navigate(['/cytology-evaluation', evaluation.id], { replaceUrl: true });
  }

  startNewEvaluation() {
    this.evaluation = null;
    this.errorMessage = '';
    this.buildForm();
    this.subscribeToValueChanges();
    this.recalculateTotals();
    this.router.navigate(['/cytology-evaluation'], { replaceUrl: true });
  }

  onAssignedToSelected(user: UserSearchResult | null) {
    this.form.patchValue({ assignedToUserId: user?.userId ?? null });
  }

  onCytologyPersonnelSelected(user: UserSearchResult | null) {
    this.form.patchValue({ cytologyPersonnelUserId: user?.userId ?? null });
  }

  onPathologistSelected(user: UserSearchResult | null) {
    this.form.patchValue({ pathologistUserId: user?.userId ?? null });
  }

  onFellowSelected(user: UserSearchResult | null) {
    this.form.patchValue({ fellowUserId: user?.userId ?? null });
  }

  onResidentSelected(user: UserSearchResult | null) {
    this.form.patchValue({ residentUserId: user?.userId ?? null });
  }

  private buildPayload(): CytologyEvaluationSavePayload {
    const raw = this.form.value;
    const sites: CytologyEvaluationSiteInput[] = (raw.sites || []).map((site: any) => ({
      id: site.id ?? null,
      site: site.site || null,
      evalEpisodeNumber: site.evalEpisodeNumber ?? null,
      adequacy: site.adequacy || null,
      dqCount: Number(site.dqCount) || 0,
      papCount: Number(site.papCount) || 0,
      thinPrepCount: Number(site.thinPrepCount) || 0,
      cellBlockCount: Number(site.cellBlockCount) || 0,
      unstainedSlidesCount: Number(site.unstainedSlidesCount) || 0
    }));

    return {
      patientIdentifiers: raw.patientIdentifiers || null,
      procedureType: raw.procedureType || null,
      procedurePerformedBy: raw.procedurePerformedBy || null,
      evaluationPerformedBy: raw.evaluationPerformedBy || null,
      viaTelecytology: !!raw.viaTelecytology,
      readLocation: raw.readLocation || null,
      procedureLocation: raw.procedureLocation || null,
      assignedToUserId: raw.assignedToUserId || null,
      clinicalHistory: raw.clinicalHistory || null,
      notes: raw.notes || null,
      patientHistory: raw.patientHistory || null,
      cytologyPersonnelUserId: raw.cytologyPersonnelUserId || null,
      pathologistUserId: raw.pathologistUserId || null,
      fellowUserId: raw.fellowUserId || null,
      residentUserId: raw.residentUserId || null,
      totalTimeSpentMinutes: raw.totalTimeSpentMinutes ?? null,
      sites
    };
  }

  async onSave() {
    if (this.readonlyMode) {
      return;
    }
    if (this.form.invalid) {
      this.errorMessage = 'Please correct the errors and try again.';
      return;
    }
    this.saving = true;
    const saved = await this.persistCurrentForm();
    this.saving = false;

    if (saved) {
      this.toastService.showSuccessToast(
        this.wasNewOnLastSave ? 'Evaluation created' : 'Evaluation saved',
        'The cytology evaluation has been saved.',
        []
      );
      await this.loadMyEvaluations();
    } else {
      this.toastService.showErrorToast('Unable to save', 'Please correct any errors and try again.', []);
    }
  }

  /**
   * Persists whatever is currently in the form (create or update) so that
   * server-side validation (e.g. required-site checks) always sees the
   * user's latest, possibly-unsaved, edits. Returns true on success.
   */
  private async persistCurrentForm(): Promise<boolean> {
    if (this.form.invalid) {
      this.errorMessage = 'Please correct the errors and try again.';
      return false;
    }
    this.errorMessage = '';
    const payload = this.buildPayload();
    const isNew = !this.evaluation;
    const result: any = this.evaluation
      ? await this.cytologyEvaluationService.save(this.evaluation.id, payload)
      : await this.cytologyEvaluationService.create(payload);
    if (result?.status) {
      this.wasNewOnLastSave = isNew;
      this.applyEvaluation(result.data);
      return true;
    }
    return false;
  }

  /**
   * Backend validation failures (DataException) come back as a 510 response
   * with a plain-text body, not JSON, so `err.error` is typically the raw
   * message string rather than an object with a `.detail` property. Handle
   * both shapes so the user actually sees the specific reason.
   */
  private extractErrorMessage(result: any, fallback: string): string {
    const errBody = result?.err?.error;
    if (typeof errBody === 'string' && errBody.trim()) {
      return errBody;
    }
    if (errBody?.detail) {
      return errBody.detail;
    }
    return fallback;
  }

  async onPrelimVerify() {
    if (!this.evaluation) {
      return;
    }
    this.prelimVerifying = true;
    // Save any unsaved edits first so the verification check reflects what's on screen.
    const saved = await this.persistCurrentForm();
    if (!saved) {
      this.prelimVerifying = false;
      this.toastService.showErrorToast(
        'Unable to preliminary verify',
        'Please correct any errors and try again before verifying.',
        []
      );
      return;
    }
    const result: any = await this.cytologyEvaluationService.prelimVerify(this.evaluation.id);
    this.prelimVerifying = false;
    if (result?.status) {
      this.applyEvaluation(result.data);
      this.toastService.showSuccessToast('Preliminary verified', 'The evaluation has been preliminarily verified.', []);
      await this.loadMyEvaluations();
    } else {
      this.toastService.showErrorToast(
        'Unable to preliminary verify',
        this.extractErrorMessage(result, 'Please ensure all required fields are complete.'),
        []
      );
    }
  }

  async onFinalVerify() {
    if (!this.evaluation) {
      return;
    }
    this.finalVerifying = true;
    // Save any unsaved edits first so the verification check reflects what's on screen.
    const saved = await this.persistCurrentForm();
    if (!saved) {
      this.finalVerifying = false;
      this.toastService.showErrorToast(
        'Unable to final verify',
        'Please correct any errors and try again before verifying.',
        []
      );
      return;
    }
    const result: any = await this.cytologyEvaluationService.finalVerify(this.evaluation.id);
    this.finalVerifying = false;
    if (result?.status) {
      this.applyEvaluation(result.data);
      this.toastService.showSuccessToast('Final verified', 'The evaluation has been finally verified.', []);
      await this.loadMyEvaluations();
    } else {
      this.toastService.showErrorToast(
        'Unable to final verify',
        this.extractErrorMessage(result, 'Please ensure all required fields are complete.'),
        []
      );
    }
  }

  openEvaluation(evaluation: CytologyEvaluation) {
    this.loadEvaluation(evaluation.id);
  }

  onDelete() {
    if (!this.evaluation) {
      return;
    }
    const evaluationId = this.evaluation.id;
    this.confirmDialogService.confirmThis(
      `Are you sure you want to delete Evaluation #${evaluationId}? This cannot be undone.`,
      async () => {
        this.deleting = true;
        const result: any = await this.cytologyEvaluationService.delete(evaluationId);
        this.deleting = false;
        if (result?.status) {
          this.toastService.showSuccessToast('Evaluation deleted', 'The draft evaluation has been deleted.', []);
          this.startNewEvaluation();
          await this.loadMyEvaluations();
        } else {
          this.toastService.showErrorToast(
            'Unable to delete',
            this.extractErrorMessage(result, 'Only draft evaluations you have access to can be deleted.'),
            []
          );
        }
      },
      () => {
        /* user cancelled; nothing to do */
      }
    );
  }

  viewCompletedEvaluations() {
    this.router.navigate(['/cytology-evaluation/completed']);
  }

  getStatusBadgeClasses(status: string | undefined) {
    if (status === 'Final Verified') {
      return 'badge rounded-pill bg-success';
    }
    if (status === 'Prelim Verified') {
      return 'badge rounded-pill bg-warning text-dark';
    }
    return 'badge rounded-pill bg-secondary';
  }

  trackById(index: number, item: CytologyEvaluation) {
    return item.id || index;
  }

  trackByIndex(index: number) {
    return index;
  }

  onPrint() {
    window.print();
  }
}
