// ********************* SLIDER *********************
// (function($) {
//     "use strict";
//     jQuery(document).ready(function($) {
//         var mobileSlider = $('.carousel');
//         mobileSlider.carousel({
//             interval: 8000,
//         });
//     });
// }(jQuery));

(function($) {
    "use strict";

    $(document).ready(function() {
        $('li.tab.fancyTab').on('click' ,function(){
            $('li.tab.fancyTab').removeClass('active');
            $(this).addClass("active");
        });
    });

})(jQuery);

// ******************* COUNTER *********************

$(document).ready(function() {

    var counters = $(".number");
    var countersQuantity = counters.length;
    var counter = [];

    for (i = 0; i < countersQuantity; i++) {
        counter[i] = parseInt(counters[i].innerHTML);
    }

    var count = function(start, value, id) {
        var localStart = start;
        setInterval(function() {
            if (localStart < value) {
                localStart++;
                counters[id].innerHTML = localStart;
            }
        }, 40);
    }

    for (j = 0; j < countersQuantity; j++) {
        count(0, counter[j], j);
    }
});

// ************** WORK PORTFOLIO ********************
// ****  1 ******

$(window).load(function() {
    $('.portfolioFilter a').click(function(){
        $('.portfolioFilter a').removeClass('current');
        $(this).addClass('current');
    });

var $container = $('#portfolio');
    $container.isotope({
      itemSelector: '.col-sm-4',
      layoutMode: 'fitRows'
    });
    
    $('#filters').on( 'click', 'a', function() {
      var filterValue = $(this).attr('data-filter');
      $container.isotope({ filter: filterValue });
      return false;
    });
});
// ****  2 ******

// ****************  BOTTOM TO TOP ****************************
(function($) {
    "use strict";

    $(document).ready(function() {

        $(window).scroll(function() {
            if ($(this).scrollTop() > 100) {
                $('.scrollup').fadeIn();
            } else {
                $('.scrollup').fadeOut();
            }
        });

        $('.scrollup').on("click", function() {
            $("html, body").animate({
                scrollTop: 0
            }, 300);
            return false;
        });

    });
})(jQuery);

//************************* HEADER STICKY **********************
$(window).scroll(function() {
    $edit_mode = document.getElementById('oe_main_menu_navbar');
    if ($(this).scrollTop() > 100) {
        if ($edit_mode) {
            $('header').removeClass("sticky");
        } else {
            $('header').addClass("sticky");
        }
    } else {
        $('header').removeClass("sticky");
    }
});

// *********************** FEATURE FANCY TABS ***************
$(document).ready(function() {

    var numItems = $('li.fancyTab').length;
    if (numItems == 12) {
        $("li.fancyTab").width('8.3%');
    }
    if (numItems == 11) {
        $("li.fancyTab").width('9%');
    }
    if (numItems == 10) {
        $("li.fancyTab").width('10%');
    }
    if (numItems == 9) {
        $("li.fancyTab").width('11.1%');
    }
    if (numItems == 8) {
        $("li.fancyTab").width('12.5%');
    }
    if (numItems == 7) {
        $("li.fancyTab").width('14.2%');
    }
    if (numItems == 6) {
        $("li.fancyTab").width('16.666666666666667%');
    }
    if (numItems == 5) {
        $("li.fancyTab").width('20%');
    }
    if (numItems == 4) {
        $("li.fancyTab").width('25%');
    }
    if (numItems == 3) {
        $("li.fancyTab").width('33.3%');
    }
    if (numItems == 2) {
        $("li.fancyTab").width('50%');
    }
});

$(window).load(function() {

    $('.fancyTabs').each(function() {

        var highestBox = 0;
        $('.fancyTab a', this).each(function() {

            if ($(this).height() > highestBox)
                highestBox = $(this).height();
        });

        $('.fancyTab a', this).height(highestBox);

    });
});



