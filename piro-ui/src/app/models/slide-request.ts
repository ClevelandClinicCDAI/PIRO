export type SlideRequestUrgency = 'Priority' | 'Routine';
export type SlideRequestReason = 'Sign Out' | 'Additional Testing' | 'Cap Inspection' | 'Conference' | 'QA' | 'Send Outs' | 'Tumor Board' | 'Validation';
export type SlideRequestCaseType = 'Surgical' | 'Cytology';

export interface SlideRequest {
  id: number;
  accessionNumber: string;
  caseType: SlideRequestCaseType;
  ePath?: boolean | null;
  reason?: string | null;
  requesterNotes?: string | null;
  slideRoomNotes?: string | null;
  status: string;
  urgencyStatus: SlideRequestUrgency;
  requestedAt: string;
  completedAt?: string | null;
  requestedBy?: string | null;
  requestedByNuid?: string | null;
  completedBy?: string | null;
  takenBy?: string | null;
  takenByNuid?: string | null;
}

export interface SlideRequestFormPayload {
  accessionNumber: string;
  urgencyStatus: SlideRequestUrgency;
  reason: SlideRequestReason;
  ePath?: boolean;
  requesterNotes?: string;
}
