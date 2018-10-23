//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    // 查询房东的订单信息
    $.get("/api/v1.0/user/orders?role=landlord", function (resp) {
        if(resp.errno == "0"){
             $(".orders-list").html(template("orders-list-tmpl", {orders:resp.data.orders}));
             $(".order-accept").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-accept").attr("order-id", orderId);
             });
        // 处理接单事物
            $(".modal-accept").on("click", function () {
                var orderId = $(this).attr("order-id");
                var data = {
                    action: "accept",
                };
                // 向后端发送接单的请求
                $.ajax({
                    ulr: "/api/v1.0/order"+orderId+"status",
                    data: JSON.stringify(data),
                    type: "put",
                    contentType: "application/json",
                    dataType: "json",
                    headers: {
                        "X-CSRFToken": getCookie("csrf_token")
                    },
                    success: function (resp) {
                        if(resp.errno == "4101"){
                            location.href = "login.html";
                        }else if(resp.errno == "0"){
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已接单");
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            $("#accept-modal").modal("hide");
                        }
                    }
                })
            });
            // 处理拒单事物
            $(".order-reject").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
            $(".modal-reject").on("click", function () {
                var orderId  = $(this).attr("order-id");
                var reject_reason = $("#reject-reason").val();
                if(!reject_reason) return;
                var data = {
                    action: "reject",
                    reason: reject_reason,
                };
                $.ajax({
                    url: "/api/v1.0/orders/"+orderId+"/status",
                    type: "put",
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    dataType: "json",
                    headers: {
                        "X-CSRFToken": getCookie("csrf_token")
                    },
                    success:function (resp) {
                        if(resp.errno == "4101"){
                            location.href = "login.html";
                        }else if(resp.errno == "0"){
                                 $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                                 $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                                 $("#reject-modal").modal("hide");
                        }
                    }
                });
            })
        }
    });
});