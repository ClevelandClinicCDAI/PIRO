import { Component, Input, ViewEncapsulation } from '@angular/core';

@Component({
  standalone: false,
  selector: '[app-commenttext]',
  templateUrl: './comment-text.component.html',
  styleUrls: ['./comment-text.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class CommentTextComponent {
  @Input('app-commenttext') inData: any;
  textComments: string[] = [];
  textComment: string = '';
  ngOnInit(): void {
    // this.inData = this.inData || {};
    // this.textComment = this.inData.textComments || '';
    //this.textComments.push(...this.textComment.split('  '));

    this.textComments = this.inData.textComments || [];
  }

  toPascalCase (str: string) : string{
    if (/^[a-z\d]+$/i.test(str)) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
    return str.replace(
      /([a-z\d])([a-z\d]*)/gi,
      (g0, g1, g2) => g1.toUpperCase() + g2.toLowerCase()
    ).replace(/[^a-z\d]/gi, '');
  }
}
