odoo.define('point_of_sale.DB', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');
    
    PosDB.include({
        
        genius_search_partner: function(query){
            console.log('genius_search_partner');            
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.partner_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_partner_by_id(id));
                }else{
                    break;
                }
            }
            return results;
            
        },
        _genius_partner_search_string: function(partner){
            console.log('_genius_partner_search_string');
            var str =  partner.name;
            if(partner.barcode){
                str += '|' + partner.barcode;
            }
            if(partner.address){
                str += '|' + partner.address;
            }
            if(partner.phone){
                str += '|' + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += '|' + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += '|' + partner.email;
            }
            if(partner.vat){
                str += '|' + partner.vat;
            }
            // [MMA] Add the last visit field
            if(partner.x_studio_last_visit){
                str += '|' + partner.x_studio_last_visit;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
        },
        
    });
    
});