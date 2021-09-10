** IMPORTANT **
======================================================

*To do*

*File src/odoo/addons/point_of_sale/static/src/js/db.js
*Line 231 Add
// [MMA][TODO] please find an other way to do it 
if(partner.x_studio_last_visit){
str += '|' + partner.x_studio_last_visit;
}

*File src/odoo/addons/point_of_sale/static/src/xml/pos.xml
*Line 1268 Add after <t t-name="Orderline">
<div class="orderline-container"><!-- [MMA] adding this for the tests -->
And don't forget to close the div ;)
	

