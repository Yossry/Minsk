odoo.define('odoo_vendor_portal.take_price', function (require) {
'use strict';

    require('web.dom_ready');
    var webPortal = require('portal.portal');
    var ajax = require('web.ajax');

    $('#wksubmit').on("click", function(event){
    var offerPirce = document.getElementById("inputPrice").value;
    var offerDate = document.getElementById("inputDelivery").value;
    var offerNote = document.getElementById("inputNote").value;
    var today = new Date();
    today.setHours(0,0,0,0)
    var offerDate1 = new Date(offerDate);
    offerDate1.setHours(0,0,0,0)
    if(offerPirce !== "" && $.isNumeric(offerPirce) && offerDate !== "") {
        if (offerDate1 < today) {
            alert("The  date can\'t be in the past.");
        } else {
            var userId = parseInt($('#loguser').val());
            var rfqId = parseInt($('#rfqId').val());
            ajax.jsonRpc("/update/vendorprice/", 'call', {
                'rfqId': rfqId, 'offerPrice': offerPirce, 'offerDate': offerDate, 'offerNote' : offerNote, 'vendorUserId' : userId})
            .then(function (vals){
                window.location.reload();
            });
        }
    } else {
        alert("Please enter valid details!!");
    }
    });

});
