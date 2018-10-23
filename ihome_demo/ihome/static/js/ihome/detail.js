function hrefBack() {
    history.go(-1);
}
// 用来获取url中的参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取该房屋的详细信息
    $.get("/api/v1.0/houses/" + houseId, function(resp){
        if ("0" == resp.errno) {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.data.house.img_urls, price:resp.data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house}));

            // resp.user_id为访问页面用户,resp.data.user_id为房东
            if (resp.data.user_id != resp.data.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid="+resp.data.house.hid);
                $(".book-house").show();
            }
            // 房屋照片的滚动播放
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
        }
    })
})

})