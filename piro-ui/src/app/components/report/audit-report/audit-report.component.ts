import { Component, Input } from '@angular/core';
import Chart from 'chart.js/auto';
import { ReportService } from '../../../../app/services/report.service';
import { ToastrService } from 'ngx-toastr';
//https://www.freecodecamp.org/news/how-to-integrate-chart-js-in-angular-using-data-from-a-rest-api/
@Component({
  standalone: false,
  selector: 'app-audit-report',
  templateUrl: './audit-report.component.html',
  styleUrls: ['./audit-report.component.css']
})
export class AuditReportComponent {
  chart: any = [];

  constructor(private reportService: ReportService, private toastr: ToastrService) { }

  @Input('app-audit-report') data: any;
  async ngOnInit() {
    const result = await this.reportService.getAuditTrailReport();
    if (result.status == true) {      
      this.chart = new Chart('canvas', {
        type: 'bar',
        data: {
          labels: result.data?.labels,
          datasets: [
            {
              label: result.data?.searchlabel,
              data: result.data?.search,
              borderWidth: 2,
            },
            {
              label: result.data?.caselabel,
              data: result.data?.case,
              borderWidth: 2,
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    } else {
      this.toastr.error('', 'Audit Trail Report error');
    }
  }

}
