export type SlideRequestUrgency = 'Priority' | 'Routine';
export type SlideRequestReason = 'Sign Out' | 'Additional Testing' | 'Cap Inspection' | 'Comparison' | 'Conference' | 'QA' | 'Re-review' | 'Send Outs' | 'Tumor Board' | 'Validation';
export type SlideRequestCaseType = 'Surgical' | 'Cytology';
export type SlideRequestDeliveryLocation = 'Deliver to Mailbox' | 'L25 Window Pickup' | 'Cytology L2-320';

export interface SlideRequest {
  id: number;
  accessionNumber: string;
  caseType: SlideRequestCaseType;
  ePath?: boolean | null;
  reason?: string | null;
  deliveryLocation?: string | null;
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
  deliveryLocation: SlideRequestDeliveryLocation;
  ePath?: boolean;
  requesterNotes?: string;
}
