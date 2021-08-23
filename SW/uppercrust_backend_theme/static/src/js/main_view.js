$(document).ready(function () {

    var $body = $('body'),
        $main_menu = $('#menu_toggle'),
        $child_menu = $('#children_toggle'),
        $right_panel = $('.ad_rightbar'),
        $width = $(document).width();

    // Right panel click time left menu close [start]
    $right_panel.click(function () {   
        if ($body.hasClass('nav-sm') || $body.hasClass('ad_open_childmenu')) {
            $body.removeClass('nav-sm ad_open_childmenu');
            $main_menu.removeClass('active');
            $child_menu.removeClass('active');
        }
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || ($width <= 991)) {
            $body.addClass('ad_full_view');
        }
    });
    // Right panel click time left menu close [stop]

    $(document).click(function (e) {
        if (!$(e.target).hasClass('cp_open')) {
            $('.o_cp_buttons').removeClass('cp_open');
        }
    });
    //Mobile view detect
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        $('body').addClass('ad_mobile ad_full_view');
    }
    if ($width <= 768) {
        $body.addClass('ad_full_view');
    }
});