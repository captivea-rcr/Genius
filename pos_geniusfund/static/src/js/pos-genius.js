odoo.define('pos_geniusfund.genius', function (require) {
"use strict";
    
    //Try massive requirements - as in vouchers_pos module
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var pos_model = require('point_of_sale.models');
    var pos_popup = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var ScreenWidget = screens.ScreenWidget;
    var models = pos_model.PosModel.prototype.models;
    var PosModelSuper = pos_model.PosModel;
    var OrderSuper = pos_model.Order;
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;    
    var QWeb = core.qweb;
    var chrome = require('point_of_sale.chrome');
    
    var thcLimit = 28.5;
    var concentrateLimit = 8;
    

    screens.OrderWidget.include({

        update_summary: function() {
            this._super();
            var order = this.pos.get('selectedOrder');

            /* Update Total */
            var original_price = order ? order.get_subtotal() : 0; // Is original price = subtotal
            var total_discount = order ? order.get_total_discount() : 0;
            var total_without_tax = order ? order.get_total_without_tax() : 0;
            var total_taxes = order ? order.get_total_tax() : 0;
            var total_with_tax = order ? order.get_total_with_tax() : 0;
            
            $("#summary_orig_price").text(this.format_currency(original_price));
            $("#summary_discount").text(this.format_currency(total_discount));
            $("#summary_subtotal").text(this.format_currency(total_without_tax));
            $("#summary_taxes").text(this.format_currency(total_taxes));
            $("#summary_total").text(this.format_currency(total_with_tax));            
            /* End Update Total */
            
            /* Update THC Limits */            
            var new_thc         = parseFloat($("#actual_thc_today").val());
            var new_concentrate = parseFloat($("#actual_concentrate_today").val());

            new_thc += order.get_thc_quantities();
            var diff_thc = parseFloat(thcLimit-new_thc);
            $('#new_thc_today').text(new_thc.toFixed(2));
            $('#thc_left').text(diff_thc.toFixed(2));
            get_gaugeValue(new_thc, thcLimit);
                
            new_concentrate += order.get_concentrate_quantities();
            var diff_concentrate = parseFloat(concentrateLimit-new_concentrate);
            $('#new_concentrate_today').text(new_concentrate.toFixed(2));
            $('#concentrate_left').text(diff_concentrate.toFixed(2));
            get_gaugeValue(new_concentrate, concentrateLimit);
            
            /* Ô design */
            // Payment button
            if(new_thc > thcLimit || new_concentrate > concentrateLimit){
                $('.button.pay').prop('disabled', true);
                $('.button.pay').css({"background-color": "#FCF0EF", "color": "#FF0000", "border-color": "#FCF0EF"});
                $('.pay .achtun-limits').show();
                var THCtextToRemove = '';
                var ConcentratetextToRemove = '';
                if(new_thc > thcLimit){
                    var THCtoremove = Math.abs(diff_thc.toFixed(2));
                    var THCtextToRemove = 'Remove\r\n' + THCtoremove + 'g THC\r\n';
                }
                if(new_concentrate > concentrateLimit){
                    var Concentratetoremove = Math.abs(diff_concentrate.toFixed(2));
                    var ConcentratetextToRemove = 'Remove\r\n' + Concentratetoremove + 'g Concentrate';
                }
                $('.text-btn-payment').text(THCtextToRemove + ConcentratetextToRemove); // blablabla
            }else{
                $('.button.pay').prop('disabled', false);
                $('.button.pay').css({"background-color": "#000", "color": "#00EDC2", "border-color": "#00EDC2"});
                $('.pay .achtun-limits').hide();
                $('.text-btn-payment').text('Payment');
            }
            // Orderlines & gauges colors
            if(new_thc > thcLimit){
                $(".progress .thc_gauge").css({"background-color":"#FF0000"});
                $(".orderline.8").css({"background-color":"#FCF0EF"});
                $(".orderline.8 .product-THC-content").show();
            }else{
                $(".progress .thc_gauge").css({"background-color":"#00EDC2"});
                $(".orderline.8").css({"background-color":"#FFF"});
                $(".orderline.8 .product-THC-content").hide();
            }
            if(new_concentrate > concentrateLimit){
                $(".progress .concentrate_gauge").css({"background-color":"#FF0000"});
                $(".orderline.9").css({"background-color":"#FCF0EF"});
                $(".orderline.9 .product-THC-content").show();
            }else{
                $(".progress .concentrate_gauge").css({"background-color":"#00EDC2"});
                $(".orderline.9").css({"background-color":"#FFF"});
                $(".orderline.9 .product-THC-content").hide();
            }
        },
        
        // Adding product image, plus, minus and delete buttons for each orderline
        render_orderline: function(orderline){
            var self = this;
            var image_url = this.get_product_image_url(orderline.product);
            var el_str  = QWeb.render('Orderline',{widget:this, line:orderline, image_url:image_url});
            var el_node = document.createElement('div');
                el_node.innerHTML = _.str.trim(el_str);
                el_node = el_node.childNodes[0];
                el_node.orderline = orderline;
                //el_node.addEventListener('click',this.line_click_handler); // line_click_handler Do we need to select the lines with the new design ? Perhaps for adding a note, a discount...
            
            orderline.node = el_node;
            
            var el_trash = el_node.querySelector('.btn_remove');
            var el_plus = el_node.querySelector('.btn_plus');
            var el_minus = el_node.querySelector('.btn_minus');
            var order = this.pos.get_order();
            var new_quant = orderline.get_quantity();
            var customer_display = this.pos.config.customer_display;
            
            if(el_trash){
                el_trash.addEventListener('click', (function(event) {
                    event.stopPropagation();
                    order.remove_orderline(orderline);
                    // Update the customer display onclick
                    if(customer_display){
                        self.pos.get_order().mirror_image_data();
                    }
                }).bind(this));
            }
            if(el_plus){
                el_plus.addEventListener('click', (function(event) {
                    event.stopPropagation();
                    new_quant += 1;
                    orderline.set_quantity(new_quant);
                    // Update the customer display onclick
                    if(customer_display){
                        self.pos.get_order().mirror_image_data();
                    }
                }).bind(this));
            }
            if(el_minus){
                el_minus.addEventListener('click', (function(event) {
                    event.stopPropagation();                    
                    new_quant -= 1;
                    if(new_quant == 0){
                        order.remove_orderline(orderline);
                    }else{
                        orderline.set_quantity(new_quant);
                    }
                    // Update the customer display onclick
                    if(customer_display){
                        self.pos.get_order().mirror_image_data();
                    }
                }).bind(this));
            }
            
            return el_node;
            
        },
        get_product_image_url: function(product){
            return window.location.origin + '/web/image?model=product.product&field=image_small&id='+product.id;
        },

    });
    
    screens.ProductScreenWidget.include({
        
        show: function(){
            var self = this;
            this._super();
            var order = this.pos.get('selectedOrder');
            if(order.get_client()){
                
                $(".current-customer").show();
                $(".partner_image").attr("src", "/web/image/res.partner/" + order.get_client().id + "/image_small");
                $(".name_partner").text(order.get_client().name);
                $(".partner_id").text('');
                $(".partner_dob").text(order.get_client().x_studio_date_of_birth);
                $(".partner_since").text('');
                $(".partner_last").text(order.get_client().x_studio_last_visit);
                $(".property_product_pricelist").text(order.get_client().property_product_pricelist[1]);

                $("#new_thc_today").text(order.get_client().x_studio_thc_products_today);
                $("#new_concentrate_today").text(order.get_client().x_studio_thc_products_today);

                $("#actual_thc_today").val(order.get_client().x_studio_thc_products_today);
                $("#actual_concentrate_today").val(order.get_client().x_studio_thc_products_today);
                
            }else{
                $(".current-customer").hide();
            }
        }
        
    });
    
    screens.ClientListScreenWidget.include({
        show: function(){           
            var self = this;
            var search_timeout = null;
            this._super();          
            this.$('.client-list-contents').delegate('.client-card','click',function(event){
                var idClient = parseInt($(this).data('id'));
                self.new_client = self.pos.db.get_partner_by_id(idClient);
                self.save_changes();
                self.gui.back();
            });
            
            this.$('.today').on('click',function(event){
                clearTimeout(search_timeout);
                var today = get_today_date();
                search_timeout = setTimeout(function(){
                    self.genius_perform_search(today, event.which === 13);
                },70);
            });
            
            this.$('.all-customers').on('click',function(event){
                self.genius_search_all();
            });
            
            
        },
        // I don't want to have focus on the search input
        genius_search_all: function(){
            var customers = this.pos.db.get_partners_sorted(1000);
            this.render_list(customers);
            this.$('.searchbox input')[0].value = '';
        },
        genius_perform_search: function(query, associate_result){
            var customers;
            if(query){
                customers = this.pos.db.genius_search_partner(query);
                this.display_client_details('hide');
                if ( associate_result && customers.length === 1){
                    this.new_client = customers[0];
                    this.save_changes();
                    this.gui.back();
                }
                this.render_list(customers);
            }else{
                customers = this.pos.db.get_partners_sorted();
                this.render_list(customers);
            }
        },
    });
    
    
    /* Screen for the customer orders */   
    var ScreenCustomerOrders = ScreenWidget.extend({
        
        template:'ScreenCustomerOrders',
        
        init: function(parent,options){
            this._super(parent,options);
            this.hidden = false;
        },
        
        show: function(){
            var self = this;
            this._super();
            this.renderElement();
            this.$('.back').click(function(){
                self.gui.back();
            });
            var orders = this.pos.orders;
            //this.render_list(orders);
            var search_timeout = null;
            this.$('.searchbox input').on('keypress',function(event){
                clearTimeout(search_timeout);
                var searchbox = this;

                // [MMA]
                if (event.keyCode === 13) {
                    event.preventDefault();
                    console.log('Someone have press the KeyCode 13 (enter)');

                    return true;
                    // And now we have to find the order id :))
                }else{
                    search_timeout = setTimeout(function(){
                        self.perform_search(searchbox.value, event.which === 13);
                    },70);
                }

            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
            this.$('.return_line_button').click(function(e){
                var order = $(e.target).closest(":not(td)").data('id');
                self.return_order(order);
            });
        },
        
    });
    gui.define_screen({name: 'ScreenCustomerOrders', widget: ScreenCustomerOrders});    
    
    
    /* Popup for the notes */
    var NotesPopup = pos_popup.extend({
        template:'NotesPopup',
        
        init: function(parent, options){
            this._super(parent, options);
            this.options = {};
            this.pos_reference = "";

        },
        show: function(options){
            this._super(options);            
        },
        events: {
            'click .button.cancel':  'click_cancel',
            'click .button.save': 'click_save',
        },
        click_save: function(){
            // here the code to save the note
        },
        click_cancel: function(){
            this.gui.close_popup();
        }
        
    });
    gui.define_popup({name:'NotesPopup', widget: NotesPopup});
    
    /* Popup for the profil */
    var ProfilePopup = pos_popup.extend({
        template:'ProfilePopup',
        init: function(parent, options){
            this._super(parent, options);
            this.options = {};
            this.pos_reference = "";

        },
        show: function(options){
            this._super(options);
            var client = this.pos.get('selectedClient');
        },
        renderElement: function () {
            this._super();
            var self = this;
            if(this.pos.get('selectedClient')){
                var client = this.pos.get('selectedClient');
                console.log(client);
                var rows = "<tr><td class=\"strong\">Name</td><td>" + client.name + "</td></tr>";
                rows += "<tr><td class=\"strong\">Address</td><td>" + client.address + "</td></tr>";
                rows += "<tr><td class=\"strong\">Email</td><td>" + client.email + "</td></tr>";
                rows += "<tr><td class=\"strong\">Phone</td><td>" + client.phone + "</td></tr>";
                rows += "<tr><td class=\"strong\">Age</td><td>" + get_age(client.x_studio_date_of_birth) + "</td></tr>";
                rows += "<tr class=\"ineedaline\"><td class=\"strong\">Member</td><td>" + get_since(client.create_date) + "</td></tr>";

                rows += "<tr><td colspan=\"2\"><![CDATA[&nbsp;]]></td></tr>";

                rows += "<tr><td class=\"strong\">Pricelist</td><td>" + client.property_product_pricelist[1] + "</td></tr>";
                rows += "<tr><td class=\"strong\">Medical Patient</td><td>?</td></tr>";
                rows += "<tr><td class=\"strong\">MMID</td><td>?</td></tr>";
                rows += "<tr><td class=\"strong\">YTD Spend</td><td>?</td></tr>";
                rows += "<tr class=\"ineedaline\"><td class=\"strong\">AVG Receipts</td><td>? -> avg of the customer orders amounts ?</td></tr>";

                rows += "<tr><td colspan=\"2\"><![CDATA[&nbsp;]]></td></tr>";

                rows += "<tr><td class=\"strong\">Total Visits</td><td>fx()</td></tr>";
                rows += "<tr><td class=\"strong\">First Vist</td><td>fx()</td></tr>";
                rows += "<tr><td class=\"strong\">Last Vist</td><td>fx()</td></tr>";
                rows += "<tr class=\"ineedaline\"><td class=\"strong\">Location</td><td class=\"test\">?</td></tr>";

                rows += "<tr><td colspan=\"2\"><![CDATA[&nbsp;]]></td></tr>";

                rows += "<tr><td class=\"strong\">Rewards Program</td><td>" + client.loyalty_points + "</td></tr>";            
                rows += "<tr><td colspan=\"2\"><![CDATA[&nbsp;]]></td></tr>";

                $(rows).appendTo(".table-profile tbody");
            }
        },
        events: {
            'click .button.cancel':  'click_cancel',
            'click .button.save': 'click_save',
        },
        click_save: function(){
            // here the code to save the note
        },
        click_cancel: function(){
            $(".pos .modal-dialog .popup").css({"height":"400px"});
            $(".pos .modal-dialog .popup .selection").css({"max-height":"273px"});
            this.gui.close_popup();            
        }
        
    });
    gui.define_popup({name:'ProfilePopup', widget: ProfilePopup});

    return {
        ScreenCustomerOrders: ScreenCustomerOrders,
    };
});