odoo.define('iwp_website.form', function (require) {
    "use strict";

    $(document).ready(function () {
        var manual_share_form = $(".oe_manual_share_form");

        manual_share_form.each(function () {
            var amount_elem = manual_share_form.find("#share_type");
            var qty_elem = manual_share_form.find("#quantity");
            var total_amount_elem = manual_share_form.find("#total_amount");

            function compute_total_amount() {
                var selected_index = amount_elem.prop("selectedIndex")
                if (selected_index >= 0) {
                    var amount = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .amount;
                    var quantity = qty_elem[0].value;
                    total_amount_elem[0].value = quantity * amount;
                }
            }

            amount_elem.change(compute_total_amount);
            qty_elem.change(compute_total_amount);
            compute_total_amount();
        });

        var manual_loan_form = $(".oe_manual_loan_form");

        manual_loan_form.each(function () {
            var amount_elem = manual_loan_form.find("#loan_issue");
            var qty_elem = manual_loan_form.find("#quantity");
            var total_amount_elem = manual_loan_form.find("#total_amount");

            function compute_total_amount() {
                var amount = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .face_value;
                var quantity = qty_elem[0].value;
                total_amount_elem[0].value = quantity * amount;
            }

            amount_elem.change(compute_total_amount);
            qty_elem.change(compute_total_amount);
            compute_total_amount();
        });

        var subscription_request_form = $(".oe_subscription_request_form");

        subscription_request_form.each(function () {
            var amount_elem = subscription_request_form.find("#share_type");
            var qty_elem = subscription_request_form.find("#quantity");
            var total_amount_elem = subscription_request_form
                .find("#total_amount");

            function compute_total_amount() {
                var selected_index = amount_elem.prop("selectedIndex")
                if (selected_index >= 0) {
                    var price = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .price;
                    var quantity = qty_elem[0].value;
                    total_amount_elem[0].value = quantity * price;
                }
            }

            function compute_minmax_quantity() {
                var selected_index = amount_elem.prop("selectedIndex")
                if (selected_index >= 0) {
                    var price = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .price;
                    var min_amount = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .min_amount;
                    var max_amount = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .max_amount;
                    if (min_amount) {
                        var min_qty = Math.ceil(min_amount / price);
                        qty_elem.attr("min", min_qty);
                    } else {
                        qty_elem.attr("min", 1);
                    }
                    if (max_amount >= 0) {
                        var max_qty = Math.floor(max_amount / price);
                        qty_elem.attr("max", max_qty);
                    } else {
                        qty_elem.removeAttr("max");
                    }
                }
            }

            amount_elem.change(function() {
                compute_total_amount();
                compute_minmax_quantity();
            });
            qty_elem.change(compute_total_amount);
            compute_total_amount();
            compute_minmax_quantity();
        });

        var operation_request_form = $(".oe_operation_request_form");

        operation_request_form.each(function () {
            var amount_elem = operation_request_form.find("#share_type");
            var qty_elem = operation_request_form.find("#quantity");
            var total_amount_elem = operation_request_form
                .find("#total_amount");

            function compute_total_amount() {
                var price = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .price;
                var quantity = qty_elem[0].value;
                total_amount_elem[0].value = quantity * price;
            }

            function compute_max_quantity() {
                var price = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .price;
                var owned_amount = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .owned_amount;
                if (owned_amount >= 0) {
                    var max_qty = Math.floor(owned_amount / price);
                    qty_elem.attr("max", max_qty);
                } else {
                    qty_elem.removeAttr("max");
                }
            }

            amount_elem.change(function() {
                compute_total_amount();
                compute_max_quantity();
            });
            qty_elem.change(compute_total_amount);
            compute_total_amount();
            compute_max_quantity();
        });

        var loan_issue_form = $(".oe_loan_issue_form");

        loan_issue_form.each(function () {
            var amount_elem = loan_issue_form.find("#loan_issue");
            var qty_elem = loan_issue_form.find("#quantity");
            var total_amount_elem = loan_issue_form
                .find("#total_amount");

            function compute_total_amount() {
                var selected_index = amount_elem.prop("selectedIndex")
                if (selected_index >= 0) {
                    var face_value = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .face_value;
                    var quantity = qty_elem[0].value;
                    total_amount_elem[0].value = quantity * face_value;
                }
            }

            function compute_minmax_quantity() {
                var selected_index = amount_elem.prop("selectedIndex")
                if (selected_index >= 0) {
                    var face_value = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .face_value;
                    var min_amount = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .min_amount;
                    var max_amount = amount_elem[0]
                        .options[selected_index]
                        .dataset
                        .max_amount;
                    if (min_amount) {
                        var min_qty = Math.ceil(min_amount / price);
                        qty_elem.attr("min", min_qty);
                    } else {
                        qty_elem.attr("min", 1);
                    }
                    if (max_amount >= 0) {
                        var max_qty = Math.floor(max_amount / price);
                        qty_elem.attr("max", max_qty);
                    } else {
                        qty_elem.removeAttr("max");
                    }
                }
            }

            amount_elem.change(function() {
                compute_total_amount();
                compute_minmax_quantity();
            });
            qty_elem.change(compute_total_amount);
            compute_total_amount();
            compute_minmax_quantity();
        });
    });

});
