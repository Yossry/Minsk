$( document ).ready(function() {
    console.log( "ready!" );
    "use strict";
    
    // common variable
    var windowWidth = $(window).width(),
        windowHeight = $(window).height(),
        headTag = $('head'),
        body = $('body'),
        mainNavbar = $('.onepage .header_area.navbar'),
        isMobile = windowWidth < 768;
    
    
        // Menu Line Height
        function MenuLineHeight() {
            var menuLineHeight = windowWidth * 0.05625;
            $('#top_menu > li > a, .logo_area > a').css('line-height', menuLineHeight + 'px');
            $('.home-7 .header_area').css('height', menuLineHeight + 'px');
        }
        
        MenuLineHeight();
    
    // mobile Menu area
    $('nav.mobile_menu').meanmenu({
        meanScreenWidth: '767'
    });
    $('nav.mean-nav li > a:first-child').on('click', function(){
        $('a.meanmenu-reveal').click();
    });
    
    $('.home-5 .dtable, .home-7 .dtable').css('height', 'calc(100vh - ' + windowWidth * 0.05625 + 'px)');
        
    // Owl Carousel for Main Slider
    var maintheme_slider = $('.mainSlider, .case_slider');
    maintheme_slider.owlCarousel({
        loop: true,
        margin: 30,
        autoplay: false,
        dots: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 1
            }
        }
    });

    $('.main_slider_nav .testi_next, .home-6 .main_slider_nav .testi_next').on('click', function () {
        maintheme_slider.trigger('next.owl.carousel');
    });
    $('.main_slider_nav .testi_prev, .home-6 .main_slider_nav .testi_prev').on('click', function () {
        maintheme_slider.trigger('prev.owl.carousel');
    });


    // Jquery counterUp
    $('.counter').counterUp({
        time: 3000
    });

    // jQuery Venobox
    $('a.veno').venobox({
        numeratio: true,
        infinigall: true
    });

    // team Content
    var team_slid2 = $('.team_cotent_slid');
    team_slid2.owlCarousel({
        loop: true,
        margin: 30,
        autoplay: false,
        dots: true,
        animateIn: 'fadeInDown',
        animateOut: 'fadeOutDown',
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 1
            }
        }
    });

    // team image
    var team_slid = $('.team_slid');
    team_slid.owlCarousel({
        loop: true,
        margin: 30,
        dots: true,
        mouseDrag: true,
        touchDrag: false,
        animateIn: 'fadeInLeft',
        animateOut: 'fadeOutRight',
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 1
            }
        }
    });
    $('.teamslide_nav .testi_next').on('click', function () {
        team_slid.trigger('next.owl.carousel');
    });
    $('.teamslide_nav .testi_prev').on('click', function () {
        team_slid.trigger('prev.owl.carousel');
    });

    team_slid.on('translate.owl.carousel', function (property) {
        $('.team_content .owl-dot:eq(' + property.page.index + ')').click();
    });
    team_slid2.on('translate.owl.carousel', function (property) {
        $('.team_member_photo .owl-dot:eq(' + property.page.index + ')').click();
    });
    
    // check features
    function checkFeatures() {
        var leftw = $('.ourFeaturesContent'),
            heightm = $('.checkBGFull').height();
        if (leftw.length) {
            leftw = leftw.offset().left;
            $('.checkfeature_contbg').css({
                'width': leftw + 'px',
                'height': heightm + 'px'
            });
        }
    }
    checkFeatures();
    
    // client Slider
    var client_slider = $('.client_img');
    client_slider.owlCarousel({
        loop: true,
        margin: 0,
        autoplay: false,
        dots: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 1
            }
        }
    });
    $('.clientslide_nav .testi_next').on('click', function () {
        client_slider.trigger('next.owl.carousel');
    });
    $('.clientslide_nav .testi_prev').on('click', function () {
        client_slider.trigger('prev.owl.carousel');
    });

    // client Slider
    var clientTestiSlider = $('.clientTestiSlider');
    clientTestiSlider.owlCarousel({
        loop: true,
        margin: 0,
        autoplay: true,
        dots: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 1
            }
        }
    });
    clientTestiSlider.on('translate.owl.carousel', function (property) {
        $('.client_img .owl-dot:eq(' + property.page.index + ')').click();
    });
    client_slider.on('translate.owl.carousel', function (property) {
        $('.clientTestiSlider .owl-dot:eq(' + property.page.index + ')').click();
    });
    var clientTestiSliderDot = clientTestiSlider.find('.owl-dot');
    clientTestiSliderDot.each(function () {
        var clientTestiIndex = clientTestiSliderDot.index(this);
        $(this).children('span').append(clientTestiIndex + 1);
    });
    

    // Blog Slider
    var blog_slider = $('.blog_slid');
    blog_slider.owlCarousel({
        loop: true,
        margin: 20,
        autoplay: false,
        dots: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            992: {
                items: 2
            }
        }
    });
    
    function skillAndVideoBgRight() {
        var skillAndVideoWidth = $('.skill_and_video .container').width(),
            skillAndVideoHeight = $('.skill_and_video').height(),
            skillAndVideoRightWidth = (windowWidth - skillAndVideoWidth) / 2 - 15;
        $('.video_control').css('height', skillAndVideoHeight);
        $('<style>.col-sm-7.skillBg::after{width: calc(100% + ' + skillAndVideoRightWidth + 'px);}</style>').appendTo('head');
    }
    
    //pricing table
    var specialTable = $('.all_pricing_table .special');
    $('.single_pricing').on('mouseover', function () {
        specialTable.removeClass('active');
    }).on('mouseleave', function () {
        specialTable.addClass('active');
    });
    
    
    //Contact Form Submit Button Disabled
    $('.jsSubmit_button input, .jsSubmit_button textarea').on('keyup', function () {
        var isEmpty = false;
        $('.jsSubmit_button [required]').not('.home-1 .jsSubmit_button [required]').each(function () {
            if ($(this).val() == "") {
                isEmpty = true;
            }
        });
        if (isEmpty) {
            $('.jsSubmit_button button[type="submit"]').attr('disabled', 'disabled');
        } else {
            $('.jsSubmit_button button[type="submit"]').removeAttr('disabled');
        }
    });
    
    // mean menu logo 
    function meanMenuLogo() {
        isMobile ? $('.mean-bar').prepend('<a href="index.html"><img alt="logo" src="/theme_materialab/static/src/img/logo.svg"></a>') : null ;
    }
    
    // SKILLS JS
    function RXknob(RXknobClass) {
        RXknobClass = $(RXknobClass);
        RXknobClass.each(function () {
            var $this = $(this),
                knobVal = $this.attr('data-rel'),
                knobAnimate = function () {
                    $({
                        value: 0
                    }).animate({
                        value: knobVal
                    }, {
                        duration : 2000,
                        easing   : 'swing',
                        progress : function () {
                            $this.val(Math.ceil(this.value)).trigger('change');
                        }
                    });
                };

            $this.knob({
                'draw' : function () {
                    $(this.i).val(this.cv + '%').css('font-size', '13px').css('color', '#eeeeee').css('font-family', 'Open Sans').css('font-weight', '400');
                }
            });

            $this.waypoint(knobAnimate, { offset: '80' }).waypoint(knobAnimate, { offset: 'bottom-in-view' });

        });
    }
    
    function RXprogress(RXprogressClass) {
        RXprogressClass = $(RXprogressClass);
        RXprogressClass.each(function () {
            var $this = $(this),
                progressAnimate = function () {
                    $this.toggleClass('slideInLeft');
                };
            $this.waypoint(progressAnimate, { offset: '80'}).waypoint(progressAnimate, { offset: 'bottom-in-view'});

        });
    }
    
    // /*
    // * Replace all SVG images with inline SVG
    // */
    // $('img.svg').each(function(){
    //     var $img = $(this),
    //         imgID = $img.attr('id'),
    //         imgClass = $img.attr('class'),
    //         imgURL = $img.attr('src');

    //     $.get(imgURL, function(data) {
    //         // Get the SVG tag, ignore the rest
    //         var $svg = $(data).find('svg');

    //         // Add replaced image's ID to the new SVG
    //         if(typeof imgID !== 'undefined') {
    //             $svg = $svg.attr('id', imgID);
    //         }
    //         // Add replaced image's classes to the new SVG
    //         if(typeof imgClass !== 'undefined') {
    //             $svg = $svg.attr('class', imgClass);
    //         }

    //         // Remove any invalid XML tags as per http://validator.w3.org
    //         $svg = $svg.removeAttr('xmlns:a');

    //         // Replace image with new SVG
    //         $img.replaceWith($svg);
    //     }, 'xml');

    // });

    //window load event
    $(window).load(function () {
        // Preloader-js
        $('.preloader-area').fadeOut('1000');
        
        /*Portfolio layout*/
        $('.all_work_item').isotope({
            //layoutMode: 'packery',
            itemSelector: '.mix',
            percentPosition: true
        });
        /*Portfolio filtering*/
        var triggerLi = $('.trigger li');
        triggerLi.on('click', function () {
            triggerLi.removeClass('active');
            $(this).addClass('active');
            var filterValue = $(this).attr('data-filter');
            $('.all_work_item').isotope({
                filter: filterValue
            });
        });
        
        $('.portfolio_items').isotope({
            layoutMode: 'packery',
            itemSelector: '.grid_item'
        });   
        
        //mean menu logo
        meanMenuLogo();
        
        // partner Slider
        var partner_slid = $('.partner_slider');
        partner_slid.owlCarousel({
            loop: true,
            margin: 0,
            autoplay: true,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                600: {
                    items: 3
                },
                992: {
                    items: 5
                }
            }
        });
    
        // Process Slider
        var processIconSlider = $('.tab_trigger_icon');
        processIconSlider.owlCarousel({
            loop: true,
            margin: 0,
            autoplay: true,
            mouseDrag: false,
            touchDrag: false,
            dots: true,
            center: true,
            responsive: {
                0: {
                    items: 5
                },
                600: {
                    items: 5
                },
                992: {
                    items: 5
                }
            }
        });
        var processIconUpDown = function processIconUpDown() {
            $('.owl-item').removeClass('neXt prEv');
            $('.owl-item.active.center').prev().addClass('prEv');
            $('.owl-item.active.center').next().addClass('neXt');
        };
        processIconUpDown();
        processIconSlider.on('translated.owl.carousel', processIconUpDown);

        // Process Slider
        var ProContentSlider = $('.pro_content'),
            singleTabIcon = $('.singleTabIcon i');
        ProContentSlider.owlCarousel({
            loop: true,
            margin: 0,
            autoplay: false,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                600: {
                    items: 1
                },
                992: {
                    items: 1
                }
            }
        });
        singleTabIcon.on('click', function () {
            $('.tab_trigger_icon .owl-dot:eq(' + $(this).data('index') + ')').click();
        });
        ProContentSlider.on('translate.owl.carousel', function (property) {
            $('.tab_trigger_icon .owl-dot:eq(' + property.page.index + ')').click();
        });
        processIconSlider.on('translate.owl.carousel', function (property) {
            $('.pro_content .owl-dot:eq(' + property.page.index + ')').click();
        });

        RXknob('.knob');
        RXprogress('.progress-bar');
        skillAndVideoBgRight();
        
        // Jquery Parallax
        $('.home-5 .header_paralux').parallax('50%', 0.2);
        isMobile ? null : $('.home-6 .project_area').parallax('50%', 0.2);
        $('.home-8 .project_area').parallax('50%', 0.2);
        $('.home-6 .social_btn').parallax('50%', 0.2);
        $('.home-8 .social_btn').parallax('50%', 0.2);
        $('.home-9 .project_area').parallax('50%', 0.2);
        $('.home-9 .social_btn').parallax('50%', 0.2);
        
        //setTimeout function
        setTimeout(function () {
            
            // Jquery Scroll Spay
            $('body').scrollspy({
                target: '.navbar-collapse',
                offset: 81
            });
            
            // Jquery Smooth Scroll
            $('.smoth-scroll a, .go-down').bind('click', function (event) {
                var $anchor = $(this);
                $('html, body').stop().animate({
                    scrollTop : $($anchor.attr('href')).offset().top - 80 + 'px'
                }, 1500, 'easeInOutCubic');
                event.preventDefault();
            });
            
            //Affix
            mainNavbar.affix({
                offset: {
                    top: 80
                }
            });
            
        }, 500);
    });
    
    $(window).scroll(function () {
        //affix
        if ($(window).scrollTop() >= windowHeight - 81) {
            mainNavbar.addClass('sticky');
        } else {
            mainNavbar.removeClass('sticky');
        }

    });
    
    $('.sroll_top').on('click', function () {
        $('html, body').animate({
            scrollTop: 0
        }, 4000);
        return false;
    });
    
    //Demo Color Box
    var colorTrigger = $('.colorDemo ul li'),
        colorBox = $('.colorDemo');
    colorTrigger.on('click', function(){
        var CCcolor = $(this).data('color'),
            colorList = colorTrigger.map(function() {
                return $(this).data('color');
            }).get();
        colorList = colorList.join(' ');
        body.removeClass( colorList ).addClass( CCcolor );
        colorTrigger.removeClass('active');
        $(this).addClass('active');
        
        //knob color change
        var knobColor;
        switch(CCcolor){
            case 'index-1':
                knobColor = {fgColor: '#d3dfff', bgColor: '#4073ff'}
            break;
            case 'home-2':
                knobColor = {fgColor: '#d3dfff', bgColor: '#623ac3'}
            break;
            case 'home-3':
                knobColor = {fgColor: '#72fff1', bgColor: '#03c1ae'}
            break;
        }
        $('.knob').trigger(
            'configure',
            {
                'fgColor': knobColor.fgColor,
                'bgColor': knobColor.bgColor
            }
        );
    });
    $('.colorDemo > i.icon-tools-2').on('click', function(){
        colorBox.toggleClass('open');
    });
    
    //ColorBox Time Out
    setTimeout(function(){
        colorBox.toggleClass('open');
    }, 3000);
    
    //window resize event
    $(window).resize(function () {
        windowWidth = $(window).width();
        windowHeight = $(window).height();
        isMobile = windowWidth < 768;
        checkFeatures();
        skillAndVideoBgRight();
        
        //Menu Line Height
        MenuLineHeight();
        
        //mean menu logo 
        meanMenuLogo();
    });
});