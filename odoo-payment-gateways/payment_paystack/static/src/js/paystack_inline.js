function payWithPaystack(){

    var handler = PaystackPop.setup({
      key: 'pk_test_a105ad6290711ae2af4236323a5f00b5f285318b',
      email: 'miracleaayodele@gmail.com',
      amount: 10000,


      metadata: {
         custom_fields: [
            {
                display_name: "Mobile Number",
                variable_name: "mobile_number",
                value: "+2348012345678"
            }
         ]
      },
      callback: function(response){
          alert('success. transaction ref ' );
      },
      onClose: function(){
          alert('window closed');
      }
    });
    handler.openIframe();

  }


