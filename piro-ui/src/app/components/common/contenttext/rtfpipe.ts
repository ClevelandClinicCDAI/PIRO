import { Pipe, PipeTransform } from "@angular/core";
import { EMFJS, RTFJS, WMFJS } from 'rtf.js';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { LocalStorageService } from '../../../services/localStorage.service';

@Pipe({ name: 'rtfPipe', standalone: false })
export class CatImageUrlPipe implements PipeTransform {
    //   constructor(/* inject your cache service */) {}
    
    constructor(private _sanitizer: DomSanitizer,
        private localStorageService:LocalStorageService) {
    }

    transform(text: string): Promise<SafeHtml> {    
        var type:string = 'partial';
        return this.convertToHtml(text, type, this._sanitizer);
    }

    getSearchHighlights(): Array<any> {
        var highlights: Array<any> = [];
        var searchUrlFrom: string = this.localStorageService.getSearchUrl();
        if(searchUrlFrom == '') {
            return highlights;
        }

        let params = searchUrlFrom.split('&page=');
        if(params.length > 0){
            var searchFilter = params[0].replace('searchFilter=','');
        }else{
            var searchFilter = '{}';
        }
        const arrSearchFilter = JSON.parse(searchFilter);
        if(!Array.isArray(arrSearchFilter)){
            return highlights;
        }
       
        arrSearchFilter.forEach(function myFunction(item: any, index: any, arr: any) {
            if(item.field === "final;comment;addend;microscopic" ||
            item.field === "final;comment;addend" || 
            item.field === "final"  || 
            item.field === "comment" || 
            item.field === "addend" || 
            item.field === "microscopic" ||
            item.field === "synoptic" || 
            item.field === "intraop" || 
            item.field === "gross" || 
            item.field === "resident" ||
            item.field === "clinical") {
                highlights.push(item.search);                
            }
        });
        return highlights;
    }

    highlightsAdv: Array<any> = [];
    parseRule(rule: any) {        
        var that = this;
        if(rule.rules != undefined && Array.isArray(rule.rules)) {
            rule.rules.forEach(function myFunction(item: any, index: any, arr: any) {
                that.parseRule(item);
            });
        }
        if (rule.operator === "contains") {            
            that.highlightsAdv.push(rule.value);                
        }
    }

    getAdvSearchHighlights(): Array<any> {
        var that = this;
        that.highlightsAdv = [];
        var advfilter = that.localStorageService.getAdancedFilterData();
        if (JSON.stringify(advfilter) == '{}') {
            return this.highlightsAdv;
        }

        var rules = advfilter.rules;

        if(!Array.isArray(rules)){
            return that.highlightsAdv;
        }

        rules.forEach(function myFunction(item: any, index: any, arr: any) {            
            that.parseRule(item); 
        });
        return that.highlightsAdv;
    }

    mark(value: string, type: string): any {
        var highlightsfacets: Array<any> = this.getSearchHighlights();
        // console.log("highlightsfacets: ", highlightsfacets);
        var highlightsadv: Array<any> = this.getAdvSearchHighlights();
        // console.log("highlightsadv: ", highlightsadv);
        highlightsfacets = highlightsfacets.concat(highlightsadv);
        // console.log("highlightsfacets: ", highlightsfacets);

        var highlights: Array<any> = [...new Set(highlightsfacets)];
        // console.log("highlights: ", highlights);

        if(type==='full') {            
            highlights.forEach(function myFunction(item: any, index: any, arr: any) {                 
                item = item.replace(/ /g, ".*");               
                const re = new RegExp("\\b("+ item +"\\b)", 'igm');
                value= value.replace(re, '<span class="highlighted-text">$1</span>');
            }); 
        } else{
            highlights.forEach(function myFunction(item: any, index: any, arr: any) {
                //const re = new RegExp(item, 'igm');
                item = item.replace(/ /g, ".*");
                const re = new RegExp("("+ item + ")", 'igm');                
                value= value.replace(re, '<span class="highlighted-text">$1</span>');
            });       
        }
        return value;
    }


    convertToHtml(value: any, type:string, sanitizer: DomSanitizer): Promise<SafeHtml> {
        var that = this;

        return new Promise(async function (resolve, reject) {
            try {
                if (!value.startsWith("{\\rtf1")) {
                    //Remove the font-family and font-size from style
                    value = value.replace(/font-family/g, "");
                    value = value.replace(/font-size/g, "");

                    var markedValue = that.mark(value, type);
                    // resolve(value);
                    resolve(markedValue);
                    return;
                }
                RTFJS.loggingEnabled(false);
                WMFJS.loggingEnabled(false);
                EMFJS.loggingEnabled(false);
                const doc = new RTFJS.Document(that.stringToArrayBuffer(value), {});

                const meta = doc.metadata();
                await doc.render().then(function (htmlElements) {
                    var html = htmlElements.map(u => u.outerHTML).join(' ');
                    
                    html = html.replace(/font-family/g, "");
                    html = html.replace(/font-size/g, "");

                    const searchRegExp = /text-align: right/g;
                    const replaceWith = 'text-align: left';
                    html = html.replace(searchRegExp, replaceWith);
                    var markedValue = that.mark(html, type);
                    var htmlS = sanitizer.bypassSecurityTrustHtml(markedValue);
                    // console.log(htmlS);
                    resolve(htmlS);                    
                }).catch(error => {
                    console.error(error);
                    //reject(error);
                });
            } catch (e) {
                console.error(e);
                resolve("RTF not loaded")
            }
        });
    }

    stringToArrayBuffer(string: any) {
        const buffer = new ArrayBuffer(string.length);
        const bufferView = new Uint8Array(buffer);
        for (let i = 0; i < string.length; i++) {
            bufferView[i] = string.charCodeAt(i);
        }
        return buffer;
    }
}
