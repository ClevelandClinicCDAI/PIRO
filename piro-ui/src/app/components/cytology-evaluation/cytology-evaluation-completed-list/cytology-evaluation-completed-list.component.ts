import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CytologyEvaluation } from 'src/app/models/cytology-evaluation';
import { CytologyEvaluationService } from 'src/app/services/cytology-evaluation.service';

@Component({
  standalone: false,
  selector: 'app-cytology-evaluation-completed-list',
  templateUrl: './cytology-evaluation-completed-list.component.html'
})
export class CytologyEvaluationCompletedListComponent implements OnInit {
  evaluations: CytologyEvaluation[] = [];
  loading = false;
  errorMessage = '';

  constructor(
    private cytologyEvaluationService: CytologyEvaluationService,
    private router: Router
  ) {}

  async ngOnInit() {
    await this.loadCompletedEvaluations();
  }

  async loadCompletedEvaluations() {
    this.loading = true;
    const result: any = await this.cytologyEvaluationService.listCompleted();
    this.loading = false;
    if (result?.status) {
      this.evaluations = result.data || [];
    } else {
      this.errorMessage = 'Unable to load completed evaluations.';
    }
  }

  view(evaluation: CytologyEvaluation) {
    this.router.navigate(['/cytology-evaluation', evaluation.id], {
      queryParams: { readonly: true }
    });
  }

  trackById(index: number, item: CytologyEvaluation) {
    return item.id || index;
  }
}
