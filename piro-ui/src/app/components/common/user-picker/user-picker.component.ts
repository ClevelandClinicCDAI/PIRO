import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Subject, debounceTime } from 'rxjs';
import { environment } from 'src/environments/environment';
import { UserSearchResult } from 'src/app/models/cytology-evaluation';
import { CytologyEvaluationService } from 'src/app/services/cytology-evaluation.service';

/**
 * Fast, searchable user-picker control. Debounces keystrokes and queries a
 * small `/user/search` endpoint server-side instead of loading the full
 * (potentially very long) PIRO user list into the browser.
 */
@Component({
  standalone: false,
  selector: 'app-user-picker',
  templateUrl: './user-picker.component.html',
  styleUrls: ['./user-picker.component.css'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => UserPickerComponent),
      multi: true
    }
  ]
})
export class UserPickerComponent implements ControlValueAccessor, OnChanges {
  @Input() placeholder = 'Search by name or NUID...';
  @Input() initialLabel: string | null | undefined = '';
  @Output() userSelected = new EventEmitter<UserSearchResult | null>();

  query = '';
  results: UserSearchResult[] = [];
  showResults = false;
  searching = false;
  selectedLabel = '';
  disabled = false;

  private querySubject = new Subject<string>();
  private onChange: (value: number | null) => void = () => {};
  private onTouched: () => void = () => {};

  constructor(private cytologyEvaluationService: CytologyEvaluationService) {
    this.querySubject.pipe(debounceTime(environment.debounceTime / 2)).subscribe((value: string) => {
      this.runSearch(value);
    });
  }

  writeValue(value: number | null): void {
    if (!value) {
      this.selectedLabel = '';
      this.query = '';
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['initialLabel'] && this.initialLabel && !this.selectedLabel) {
      this.selectedLabel = this.initialLabel;
      this.query = this.initialLabel;
    }
  }

  registerOnChange(fn: (value: number | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  onInput(value: string) {
    this.query = value;
    this.showResults = true;
    if (!value || value.trim().length < 2) {
      this.results = [];
      return;
    }
    this.querySubject.next(value.trim());
  }

  private async runSearch(value: string) {
    this.searching = true;
    const result: any = await this.cytologyEvaluationService.searchUsers(value);
    this.searching = false;
    this.results = result?.status ? result.data || [] : [];
  }

  select(user: UserSearchResult) {
    this.selectedLabel = `${user.lastName}, ${user.firstName} (${user.nuid})`;
    this.query = this.selectedLabel;
    this.showResults = false;
    this.results = [];
    this.onChange(user.userId);
    this.onTouched();
    this.userSelected.emit(user);
  }

  clear() {
    this.selectedLabel = '';
    this.query = '';
    this.results = [];
    this.onChange(null);
    this.onTouched();
    this.userSelected.emit(null);
  }

  blurSoon() {
    // Delay hiding results so a click on a result row registers first.
    setTimeout(() => (this.showResults = false), 200);
  }
}
