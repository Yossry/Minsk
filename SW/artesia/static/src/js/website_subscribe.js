$(document).ready(function () {
  $.fn.serializeFormJSON = function () {

        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
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

  function validateEmail(subsemail) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(subsemail);
  }

  $('#subscribe').on('click', function () {
      var form = $('#subsForm');
      datas = JSON.stringify(form.serializeArray())
      data = form.serializeFormJSON();
      required = false
      if('subsemail' in data && data['subsemail'] == '') {
        document.getElementById('subsemail');
        required = true;
      }
      if(required) {
        document.getElementById("contact_mail").innerHTML = "Sorry, We need a Email Id for Subscription. Please complete all of the required fields.";
        document.getElementById('contact_mail').style.color = "red";
        return false;
      }else if (!validateEmail(data['subsemail'])){
        document.getElementById('subsemail').style.borderColor = "red";
        document.getElementById("contact_mail").innerHTML = "Email is Invalid";
        document.getElementById('contact_mail').style.color = "red";
        return false;
      }else {
        $.ajax({
            type: "POST",
            dataType: "json",
            contentType : "application/json",
            url: '/subscribe_action',
            data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'datas' : datas}}),
            success: function (data) {
              document.getElementById("contact_mail").innerHTML = "YOUR SUBSCRIPTION HAS BEEN SENT SUCCESSFULLY";
              document.getElementById('contact_mail').style.color = "green";
              document.getElementById('subsemail').style.borderColor = "#5FBBF9";
              document.getElementById("subsForm").reset();
            },
            error: function(data){
                console.log("ERROR ", data);
            }
        });
      }
  });
});