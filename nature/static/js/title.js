(function(){
var ua = navigator.userAgent.toLocaleLowerCase();
var pf = navigator.platform.toLocaleLowerCase();
var isAndroid = (/android/i).test(ua)||((/iPhone|iPod|iPad/i).test(ua) && (/linux/i).test(pf))
    || (/ucweb.*linux/i.test(ua));
var isIOS =(/iPhone|iPod|iPad/i).test(ua) && !isAndroid;
var isWinPhone = (/Windows Phone|ZuneWP7/i).test(ua);

var mobileType = {
    pc:!isAndroid && !isIOS && !isWinPhone,
    ios:isIOS,
    android:isAndroid,
    winPhone:isWinPhone
};

if(!mobileType.pc){
    (function(){
        // $('#title').attr("src", "/static/img/Title_mobile.png");
        $('#title').remove();
        })();
}
})();