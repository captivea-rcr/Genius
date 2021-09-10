/*
Pour accéder aux objets du POS :
this.posmodel....
this.odoo...
ou si c'est possible les faire passer par la fonction
*/

function pos_genius_customer(){
    this.posmodel.gui.show_screen('clientlist');
}
function pos_genius_customer_orders(){
    this.posmodel.gui.show_screen('ScreenCustomerOrders');
}
function pos_genius_return(){
    /* Oginal function :
    var orders = this.pos.orders;
    this.gui.show_screen('orderlist',{orders:orders});
    */
    var orders = this.posmodel.orders;
    this.posmodel.gui.show_screen('orderlist',{orders:orders});
}
function pos_genius_manager_login(){
    this.posmodel.gui.show_popup(
        'confirm',
        {
            'title': 'Login as a manager ?',
            'body': 'You are connected as ' + this.odoo.session_info.username + '<br />What do we do here?  Disconnect the current user?',
        }
    );
}

function pos_genius_add_notes(){
    this.posmodel.gui.show_popup(
        'NotesPopup',
        {
            'title': 'Notes',
            'body': '<textarea name="customer_note"></texarea>',
        }
    );
}
function pos_genius_see_profile(){
    this.posmodel.gui.show_popup(
        'ProfilePopup',
        {
            'title': 'Profile',
            'body': 'test',
        }
    );
    $(".pos .modal-dialog .popup").css({"height":"650px"});
    $(".pos .modal-dialog .popup .selection").css({"max-height":"510px"});
}

function get_gaugeValue(value, coeff){
    
    var n = parseFloat(276/coeff).toFixed(2);     // 34.5 = 276px/8
    var gauge_concentrate = parseFloat(value*n).toFixed(2);
    
    if(coeff === 8){
        $('.concentrate_gauge').attr('aria-valuenow', gauge_concentrate).css('width', gauge_concentrate);
    }else{
        $('.thc_gauge').attr('aria-valuenow', gauge_concentrate).css('width', gauge_concentrate);        
    }
    
    
}
function get_age(dob){
    if(dob){
        var birthday = new Date(dob);
        var ageDifMs = Date.now() - birthday.getTime();
        var ageDate = new Date(ageDifMs); // miliseconds from epoch
        return Math.abs(ageDate.getUTCFullYear() - 1970);
    }else{
        return false;
    }
    
}
function get_since(date_creation){
    
    var date1 = new Date(date_creation);
    var date2 = new Date();

    const diffTime = Math.abs(date2.getTime() - date1.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    // Do we display only the days ?
    
    if(diffDays){
        return diffDays + ' days';
    }

}
function get_today_date(){
    
    d = new Date();
    var day = d.getDate() > 9 ? d.getDate() : '0' + d.getDate();
    var m = d.getMonth() + 1;
    var month = m > 9 ? m : '0' + m;
    
    return d.getFullYear() + '-' + month + '-' + day;
    
}