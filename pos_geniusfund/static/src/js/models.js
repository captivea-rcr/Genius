odoo.define('pos_geniusfund.models', function (require) {
  "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');    
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    models.load_fields('res.partner', ['x_studio_concentrate', 'x_studio_thc_products_today', 'x_studio_last_visit','x_studio_date_of_birth','x_studio_mmic','create_date']);
    models.load_fields('product.product', ['x_studio_thc_content_g']);
    
    
    
    models.Order = models.Order.extend({
        
        get_quantities: function(){
            
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_quantity();
            }), 0), this.pos.currency.rounding);

        },
        get_thc_quantities: function(){

            var thc_quant = 0;
            this.orderlines.each(function(orderline){                
                if(orderline.get_categ_id() == 8){
                    thc_quant += orderline.get_quantity() * orderline.get_thc_quantity();
                }                
            });            
            return thc_quant;

        },
        get_concentrate_quantities: function(){
            
            var concentrate_quant = 0;
            this.orderlines.each(function(orderline){               
                if(orderline.get_categ_id() == 9){
                    concentrate_quant += orderline.get_quantity() * orderline.get_thc_quantity();
                }                
            });            
            return concentrate_quant;
  
        },

    });
    
    models.Orderline = models.Orderline.extend({
        
        get_thc_quantity: function(){
            return this.get_product().x_studio_thc_content_g; 
        },
        get_concentrate_quantity: function(){
            return this.get_product().x_studio_thc_content_g;
        },
        get_categ_id: function(){
            return this.get_product().categ_id[0];
        }

    });

});