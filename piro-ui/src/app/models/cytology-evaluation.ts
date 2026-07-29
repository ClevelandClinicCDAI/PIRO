export type CytologyEvaluationStatus = 'Draft' | 'Prelim Verified' | 'Final Verified';

export interface CytologyEvaluationSite {
  id: number;
  site?: string | null;
  evalEpisodeNumber?: number | null;
  adequacy?: string | null;
  dqCount: number;
  papCount: number;
  thinPrepCount: number;
  cellBlockCount: number;
  unstainedSlidesCount: number;
  sortOrder: number;
}

export interface CytologyEvaluationSiteInput {
  id?: number | null;
  site?: string | null;
  evalEpisodeNumber?: number | null;
  adequacy?: string | null;
  dqCount: number;
  papCount: number;
  thinPrepCount: number;
  cellBlockCount: number;
  unstainedSlidesCount: number;
}

export interface CytologyEvaluationTotals {
  totalDQ: number;
  totalPap: number;
  totalThinPrep: number;
  totalCellBlock: number;
  totalUnstainedSlides: number;
}

export interface CytologyEvaluationSavePayload {
  patientIdentifiers?: string | null;
  procedureType?: string | null;
  procedurePerformedBy?: string | null;
  evaluationPerformedBy?: string | null;
  viaTelecytology?: boolean | null;
  readLocation?: string | null;
  procedureLocation?: string | null;
  assignedToUserId?: number | null;
  clinicalHistory?: string | null;
  notes?: string | null;
  patientHistory?: string | null;
  cytologyPersonnelUserId?: number | null;
  pathologistUserId?: number | null;
  fellowUserId?: number | null;
  residentUserId?: number | null;
  totalTimeSpentMinutes?: number | null;
  sites: CytologyEvaluationSiteInput[];
}

export interface CytologyEvaluation extends CytologyEvaluationSavePayload {
  id: number;
  status: CytologyEvaluationStatus;
  assignedToName?: string | null;
  cytologyPersonnelName?: string | null;
  pathologistName?: string | null;
  fellowName?: string | null;
  residentName?: string | null;
  prelimVerifierNuid?: string | null;
  prelimVerifierName?: string | null;
  prelimVerifiedDate?: string | null;
  finalVerifierNuid?: string | null;
  finalVerifierName?: string | null;
  finalVerifiedDate?: string | null;
  createDate: string;
  updateDate?: string | null;
  sites: CytologyEvaluationSite[];
  totals: CytologyEvaluationTotals;
}

export interface CytologyTerminology {
  procedureType: string[];
  readLocation: string[];
  procedureLocation: string[];
  site: string[];
  adequacy: string[];
}

export interface UserSearchResult {
  userId: number;
  nuid: string;
  firstName: string;
  lastName: string;
}
