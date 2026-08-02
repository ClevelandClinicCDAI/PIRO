import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ExtractionService } from '../../../services/extraction.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-extraction-sessions',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './extraction-sessions.component.html',
  styleUrls: ['./extraction-sessions.component.css']
})
export class ExtractionSessionsComponent implements OnInit {
  sessions: any[] = [];
  loading = true;
  newSessionName = '';
  creating = false;

  constructor(
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
    } catch (e) {
      this.toastr.error('Failed to load extraction sessions.');
    } finally {
      this.loading = false;
    }
  }

  async createSession() {
    if (!this.newSessionName.trim()) return;
    this.creating = true;
    try {
      const session = await this.extractionService.createSession(this.newSessionName.trim());
      this.newSessionName = '';
      this.router.navigate(['/extraction/schema', session.ExtractionSessionId]);
    } catch (e) {
      this.toastr.error('Failed to create session.');
    } finally {
      this.creating = false;
    }
  }

  openSchema(sessionId: number) {
    this.router.navigate(['/extraction/schema', sessionId]);
  }

  openReview(sessionId: number) {
    this.router.navigate(['/extraction/review', sessionId]);
  }

  async deleteSession(session: any) {
    if (!confirm(`Delete session "${session.Name}"?`)) return;
    try {
      await this.extractionService.deleteSession(session.ExtractionSessionId);
      this.sessions = this.sessions.filter(s => s.ExtractionSessionId !== session.ExtractionSessionId);
      this.toastr.success('Session deleted.');
    } catch (e) {
      this.toastr.error('Failed to delete session.');
    }
  }

  statusClass(status: string): string {
    switch (status) {
      case 'completed': return 'badge bg-success';
      case 'completed_with_errors': return 'badge bg-warning text-dark';
      case 'running': return 'badge bg-primary';
      case 'failed': return 'badge bg-danger';
      default: return 'badge bg-secondary';
    }
  }

  statusLabel(status: string): string {
    switch (status) {
      case 'draft': return 'Draft';
      case 'running': return 'Running';
      case 'completed': return 'Completed';
      case 'completed_with_errors': return 'Done (with errors)';
      case 'failed': return 'Failed';
      default: return status;
    }
  }
}
