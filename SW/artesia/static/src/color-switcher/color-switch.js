(function ($) {
 "use strict";

	$(document).ready(function() {
		$('.styleswitch').on('click' ,function(){
			switchStylestyle(this.getAttribute("data-rel"));
			$(".predefined_styles div").removeClass("selected");
			$(this.getElementsByTagName('div')).addClass("selected");
			return false;	
		});
		var c = readCookie('style');
		if (c) switchStylestyle(c);
	});

	function switchStylestyle(styleName){
		$('link[rel*=style][title]').each(function(i){
			this.disabled = true;
			if (this.getAttribute('title') == styleName) this.disabled = false;
		});
		createCookie('style', styleName, 365);
	}

	// Cookie functions
	function createCookie(name,value,days){
		if (days){
			var date = new Date();
			date.setTime(date.getTime()+(days*24*60*60*1000));
			var expires = "; expires="+date.toGMTString();
		}
		else var expires = "";
		document.cookie = name+"="+value+expires+"; path=/";
	}
	function readCookie(name){
		var nameEQ = name + "=";
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++){
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1,c.length);
			if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
		}
		return null;
	}
	function eraseCookie(name){
		createCookie(name,"",-1);
	}
	
	$(document).ready(function() {
		$('.demo_changer .demo-icon').on('click' ,function(){
			if($('.demo_changer').hasClass("active")){
				$('.demo_changer').animate({"left":"-260px"},function(){
					$('.demo_changer').toggleClass("active");
				});						
			}else{
				$('.demo_changer').animate({"left":"0px"},function(){
					$('.demo_changer').toggleClass("active");
				});			
			} 
		});
	});

	$(document).ready(function() {
		$('.panel-layout-boxed').on("click",function(){
			$('body').addClass( 'boxed' );
			return false;
		});

		$('.panel-layout-reset').on("click",function(){
			$('body').removeClass( 'boxed' );
			return false;
		});
	});
})(jQuery);