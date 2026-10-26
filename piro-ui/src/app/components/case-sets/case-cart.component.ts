import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { CaseCartService } from '../../services/case-cart.service';
import { CaseSetService, caseSetError } from '../../services/case-set.service';

@Component({
  selector: 'app-case-cart', standalone: true, imports: [CommonModule, FormsModule],
  templateUrl: './case-cart.component.html',
  styles: ['.cart-cases { max-height: 16rem; overflow-y: auto; }']
})
export class CaseCartComponent implements OnInit {
  mode: 'NEW' | 'EXISTING' = 'NEW';
  name = ''; description = ''; targetId: number | null = null;
  targets: {id: number; name: string}[] = [];
  loading = false; busy = false; error = ''; targetsError = '';
  constructor(public cart: CaseCartService, private api: CaseSetService, public modal: NgbActiveModal) {}
  ngOnInit() { return this.loadTargets(); }
  async loadTargets() {
    this.loading = true; this.targetsError = '';
    try { this.targets = await this.api.cartTargets(); }
    catch (error) { this.targetsError = caseSetError(error); }
    finally { this.loading = false; }
  }
  async save() {
    const caseIds = this.cart.items.map(item => item.caseId);
    if (this.busy || !caseIds.length || (this.mode === 'NEW' ? !this.name.trim() : !this.targetId || this.loading || !!this.targetsError)) return;
    this.busy = true; this.error = '';
    try {
      const result = this.mode === 'NEW'
        ? {set: await this.api.createFromCart(this.cart.creation(this.name.trim(), this.description, caseIds)), added: caseIds.length, alreadyPresent: 0}
        : await this.api.addCases(Number(this.targetId), caseIds);
      this.cart.remove(caseIds);
      this.cart.completeCreation();
      this.modal.close(result);
    } catch (error) { this.error = caseSetError(error); }
    finally { this.busy = false; }
  }
}
