export type SlideRequestUrgency = 'SameDay' | 'Routine';

export interface SlideRequest {
  id: number;
  accessionNumber: string;
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
  requesterNotes?: string;
}
