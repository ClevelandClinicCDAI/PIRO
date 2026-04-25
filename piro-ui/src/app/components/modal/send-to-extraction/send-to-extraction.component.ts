import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ExtractionService } from '../../../services/extraction.service';

@Component({
  selector: 'app-send-to-extraction',
  templateUrl: './send-to-extraction.component.html',
  styleUrls: ['./send-to-extraction.component.css']
})
export class SendToExtractionComponent implements OnInit {
  /** Array of CaseIds to add to the extraction queue */
  @Input() caseIds: number[] = [];

  sessions: any[] = [];
  selectedSessionId: number | null = null;
  newSessionName = '';
  mode: 'existing' | 'new' = 'new';
  loading = false;
  sending = false;

  constructor(
    public modal: NgbActiveModal,
    private extractionService: ExtractionService,
    private router: Router,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.loadSessions();
  }

  async loadSessions() {
    this.loading = true;
    try {
      this.sessions = await this.extractionService.getSessions() ?? [];
      if (this.sessions.length > 0) {
        this.mode = 'existing';
        this.selectedSessionId = this.sessions[0].ExtractionSessionId;
      }
    } catch {
      // ignore — new session mode is the fallback
    } finally {
      this.loading = false;
    }
  }

  async send() {
    this.sending = true;
    try {
      let sessionId: number;

      if (this.mode === 'new') {
        const name = this.newSessionName.trim() || `Extraction ${new Date().toLocaleDateString()}`;
        const session = await this.extractionService.createSession(name);
        sessionId = session.ExtractionSessionId;
      } else {
        if (!this.selectedSessionId) {
          this.toastr.warning('Please select a session.');
          return;
        }
        sessionId = this.selectedSessionId;
      }

      await this.extractionService.addToQueue(sessionId, this.caseIds);

      const caseWord = this.caseIds.length === 1 ? 'case' : 'cases';
      this.toastr.success(
        `${this.caseIds.length} ${caseWord} added to extraction queue.`,
        'Sent to Extraction Suite'
      );

      this.modal.close(sessionId);
      this.router.navigate(['/extraction/schema', sessionId]);
    } catch (e) {
      this.toastr.error('Failed to send cases to extraction queue.');
    } finally {
      this.sending = false;
    }
  }
}
