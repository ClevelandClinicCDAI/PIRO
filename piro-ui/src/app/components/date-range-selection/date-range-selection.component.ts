import { Component, EventEmitter, HostListener, Input, OnInit, Output, ViewChild } from '@angular/core';
import { NgbDateStruct, NgbInputDatepicker } from '@ng-bootstrap/ng-bootstrap';
import moment from 'moment';
import { Common } from '../../helpers';
@Component({
  standalone: false,
  selector: 'app-date-range-selection',
  templateUrl: './date-range-selection.component.html',
  styleUrls: ['./date-range-selection.component.scss'],
})
export class DateRangeSelectionComponent implements OnInit {

  @ViewChild('dp') private datePicker!: NgbInputDatepicker;
  @Input() from!: any;
  @Input() to!: any;
  @Input() placeholder = 'starting today';
  @Output() dateRangeSelection = new EventEmitter<{ from: Date, to: Date }>();
  hoveredDate!: Date | null;
  isOpen = false;
  // from: any;
  // to: any;
  // @HostListener('document:click', ['$event.target']) onClick(element:any) {
  //   const host = document.getElementById('dateRangePicker');
  //   if (this.datePicker && this.isOpen && !this.isDescendant(host, element)) {
  //     this.emit(true);
  //   }
  // }

  constructor(private common: Common) { }

  ngOnInit() {
    // console.log(this.from)
    // console.log(this.to)
  }

  private emit(close?: boolean) {
    const dateRange: any = {
      from: this.from,
      to: this.to,
    };

    this.dateRangeSelection.emit(dateRange);

    // if (close) {
    //   this.isOpen = false;
    //   this.datePicker.close();
    // }
  }

  /**
   * Check whether or not an element is a child of another element
   *
   * @private
   * @param {any} parent
   * @param {any} child
   * @returns if child is a descendant of parent
   * @memberof DateRangeSelectionComponent
   */
  // private isDescendant(parent:any, child:any) {
  //   let node = child;
  //   while (node !== null) {
  //     if (node === parent) {
  //       return true;
  //     } else {
  //       node = node.parentNode;
  //     }
  //   }
  //   return false;
  // }

  // get formattedDateRange(): string {
  //   if (!this.from) {
  //     return `missing start date`;
  //   }

  //   const fromFormatted = moment(this.from).format('MM/DD/YYYY');

  //   return this.to
  //     ? `${fromFormatted}`
  //     + ` - `
  //     + `${moment(this.to).format('MM/DD/YYYY')}`
  //     : `${fromFormatted}`;

  // }

  // onDateSelection(date: NgbDateStruct) {
  //   console.log("date: ", date);
  //   if (!this.from && !this.to) {
  //     this.from = this.toDate(date);
  //   } else if (this.from && !this.to && this.toMoment(date).isAfter(this.from)) {
  //     this.to = this.toDate(date);
  //     this.emit(true);
  //   } else {
  //     this.to = null;
  //     this.from = this.toDate(date);
  //   }
  // }

  toDate(dateStruct: NgbDateStruct): Date | null {
    return dateStruct ? new Date(dateStruct.year, dateStruct.month - 1, dateStruct.day) : null;
  }

  toMoment(dateStruct: NgbDateStruct): moment.Moment {
    return moment(this.toDate(dateStruct));
  }

  isHovered = (date: NgbDateStruct) => this.from && !this.to && this.hoveredDate
    && this.toMoment(date).isAfter(this.from) && this.toMoment(date).isBefore(this.hoveredDate);

  isInside = (date: NgbDateStruct) => this.toMoment(date).isAfter(moment(this.from).startOf('day')) && this.toMoment(date).isBefore(moment(this.to).startOf('day'));
  isFrom = (date: NgbDateStruct) => this.toMoment(date).isSame(this.from, 'd');
  isTo = (date: NgbDateStruct) => this.toMoment(date).isSame(this.to, 'd');
  
  onBlurDateSelection() {
    var dateFrom = (<HTMLInputElement>document.getElementById('dateFrom')).value;
    var dateTo = (<HTMLInputElement>document.getElementById('dateTo')).value;

    if (!isNaN(new Date(dateFrom).getDate()) && 
    !isNaN(new Date(dateTo).getDate())) {
      this.from = dateFrom;
      this.to = dateTo;
      if (this.from && this.to) {
        this.emit(true);
      }
    }
  }

  onFromDateSelection(date: NgbDateStruct) {
    this.from = this.common.formatDate(new Date(date.year, date.month - 1, date.day));
    if (this.from && this.to) {
      this.emit(true);
    }
  } 

  onToDateSelection(date: NgbDateStruct) {
    this.to = this.common.formatDate(new Date(date.year, date.month - 1, date.day));
    if (this.from && this.to) {
      this.emit(true);
    }
  }
}
