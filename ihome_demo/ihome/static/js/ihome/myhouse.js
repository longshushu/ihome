$(document).ready(function(){
    // 向后端发送数据确认是否进行实名认证
    $.get("api/v1.0/user/auth", function (resp) {
        if(resp.errno == "4101"){
           // 为登录，跳转到登录页面
            href.location="login.html"
        }else if(resp.errno =="0"){
            if(!resp.data.real_name && resp.data.id_card){
                $(".auth-warn").show();
                return;
            }
            // 向前端发送信息获取用户的房源的信息
            $.get("api/v1.0/user/houses",function (resp) {
                if(resp.errno == "0"){
                    $("#houses-list").html(template("houses-list-tmpl", {houses:resp.data.houses}))
                }else{
                     $("#houses-list").html(template("houses-list-tmpl", {houses:[]}));
                }
            });
        }
    });


})