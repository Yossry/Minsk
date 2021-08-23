$(document).ready(function() {
    $.fn.serializeFormJSON = function() {

        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    function validateEmail(email) {
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }

    $('#submit_button').on('click', function() {
        var form = $('#contact-form');
        datas = JSON.stringify(form.serializeArray())
        data = form.serializeFormJSON();
        required = false
        if ('name' in data && data['name'] == '') {
            document.getElementById('name').style.borderColor = "red";
            required = true;
        }
        if ('email' in data && data['email'] == '') {
            document.getElementById('email').style.borderColor = "red";
            required = true;
        }
        if ('mobile' in data && data['mobile'] == '') {
            document.getElementById('mobile').style.borderColor = "red";
            required = true;
        }
        if ('message' in data && data['message'] == '') {
            document.getElementById('message').style.borderColor = "red";
            required = true;
        }
        if (required) {
            document.getElementById("contact_message").innerHTML = "Sorry, we need a little more information. Please complete all of the required fields.";
            document.getElementById('contact_message').style.color = "red";
            return false;
        } else if (!validateEmail(data['email'])) {
            document.getElementById('email').style.borderColor = "red";
            document.getElementById("contact_message").innerHTML = "Email is invalid";
            document.getElementById('contact_message').style.color = "red";
            document.getElementById('name').style.borderColor = "#2A2A2A";
            document.getElementById('mobile').style.borderColor = "#2A2A2A";
            document.getElementById('message').style.borderColor = "#2A2A2A";
            return false;
        } else {
            $.ajax({
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                url: '/contactform_action',
                data: JSON.stringify({
                    'jsonrpc': "2.0",
                    'method': "call",
                    "params": {
                        'datas': datas
                    }
                }),
                success: function(data) {
                    document.getElementById("contact_message").innerHTML = "YOUR CONTACT HAS BEEN SENT SUCCESSFULLY";
                    document.getElementById('contact_message').style.color = "green";
                    document.getElementById("contact-form").reset();
                },
                error: function(data) {
                    console.log("ERROR ", data);
                }
            });
        }
    });
});