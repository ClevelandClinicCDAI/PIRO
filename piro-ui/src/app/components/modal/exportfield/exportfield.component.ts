import { Component, Input } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { DataService } from '../../../services/data.service';
import { ToastrService } from 'ngx-toastr';
import { ExtractRequestService } from '../../../services/extract-request.service';

@Component({
  selector: 'app-exportfield',
  templateUrl: './exportfield.component.html',
  styleUrls: ['./exportfield.component.css']
})
export class ExportfieldComponent {

  // exportfieldForm: any = FormGroup;
  submitted = false;
  query: string = ''
  fields: any = [];
  categories: any = [];
  showError: boolean = false;
  skeltoncards: any = [1, 2, 3, 4];
  contentLoaded: boolean = false;
  selectedFields: any = [];
  removedFields: any = [];
  // get f() { return this.exportfieldForm.controls; }

  @Input() inSelectedFields: any = [];
  @Input() searchRequestId: number = -1;
  @Input() isCreate: boolean = false;
  @Input() isUpdate: boolean = false;
  @Input() isReadonly: boolean = false;
  constructor(private activeModal: NgbActiveModal,
    private formBuilder: FormBuilder,
    private dataservice: DataService,
    private extractRequestService: ExtractRequestService,
    private toastr: ToastrService) {

  }

  async ngOnInit() {

    const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
    // await sleep(1000);
    if (this.isCreate) {
      this.selectedFields = [...this.inSelectedFields];

      var dataFields: any = await this.extractRequestService.getDataFields();
      if (dataFields!.status) {
        this.categories = dataFields.data.categories;
        this.fields = dataFields.data.fields;
        this.contentLoaded = true;
      }
    } else if (this.isUpdate) {
      //fetch the data
      var dataFields: any = await this.extractRequestService.getDataFieldsForRequest(this.searchRequestId);
      if (dataFields!.status) {
        this.selectedFields = dataFields.data.filter((item: any) => item.selected === true);//dataFields.data;
      }

      var dataFields: any = await this.extractRequestService.getDataFields();
      if (dataFields!.status) {
        this.categories = dataFields.data.categories;
        this.fields = dataFields.data.fields;
        this.contentLoaded = true;
      }
    } else if (this.isReadonly) {
      //fetch the data
      var dataFields: any = await this.extractRequestService.getDataFieldsForRequest(this.searchRequestId);
      if (dataFields!.status) {
        this.selectedFields = dataFields.data.filter((item: any) => item.selected === true);
        this.removedFields = dataFields.data.filter((item: any) => item.selected === false);
        this.contentLoaded = true;
      }
    }


  }

  closeModal() {
    this.activeModal.close([]);
  }

  // convertToValue(key: string) {
  //   var arr: any = [];
  //   this.exportfieldForm.value[key].map((x: any, i: any) => {
  //     if (x) {
  //       arr.push(this.fields[i]);
  //     }
  //   })
  //   return arr;
  // }

  checkSelected(id: any): boolean {
    var selArr = this.selectedFields.filter(function (field: any) {
      return field.datafieldId == id;
    });
    return selArr.length > 0;
  }

  onclear() {
    this.selectedFields = [];
    // var checked = document.querySelectorAll('input:checked.selcolumn');
    // for (var i = 0; i < checked.length; ++i) { 
    //   checked[i].remo .removeAttribute("checked");
    // }
  }

  oncategory(category: any) {
    var that = this
    var fieldArr = that.fields.filter(function (field: any) {
      return field.categoryid == category.categoryid;
    });

    var selArr = that.selectedFields.filter(function (field: any) {
      return field.categoryid == category.categoryid;
    });
    var fieldIds: any = [];
    //if there are previous selection, clear them
    if (selArr.length > 0) {
      selArr.forEach(function (field: any) {
        fieldIds.push(field.datafieldId)
      });

      fieldIds.forEach(function (fieldId: any) {
        // const index = that.selectedFields.indexOf(field);
        var matchedIndex = that.selectedFields.map(function (obj: any) { return obj.datafieldId; }).indexOf(fieldId);

        if (matchedIndex > -1) {
          that.selectedFields.splice(matchedIndex, 1);
        }
      });
    } else {
      //If there are no selection for the category, add them
      fieldArr.forEach(function (field: any) {
        that.oncheck(field);
      });
    }
  }


  oncheck(fieldSelected: any) {
    var selArr = this.selectedFields.filter(function (field: any) {
      return field.datafieldId == fieldSelected.datafieldId;
    });
    if (selArr.length == 0) {
      this.selectedFields.push(fieldSelected);
    } else {
      const index = this.selectedFields.indexOf(selArr[0]);
      if (index > -1) {
        this.selectedFields.splice(index, 1);
      }
    }
  }

  async onsubmit() {
    this.showError = false;     
    if (this.isCreate) {
      if (this.selectedFields.length > 0) {
        this.activeModal.close(this.selectedFields);
      } else {
        this.showError = true;
      }
    } else if (this.isUpdate) {
      if (this.selectedFields.length > 0) {
        var fieldIds = this.selectedFields.map(function (item: any) { return item.datafieldId; });
        var save: any = await this.extractRequestService.saveDataFieldsForRequest(this.searchRequestId, fieldIds);
        if (save!.status) {
          this.toastr.success('', 'Data saved successfully');
          this.activeModal.close(this.selectedFields);
        }
        else {
          this.toastr.error('', 'Something went wrong.');
        }
      } else {
        this.showError = true;
      }
    }
  }
}