function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(document).ready(function () {
    // 在页面加载时向后端发送请求数据
    // $.get("/api/v1.0/user", function (resp) {
    //     // 用户未登录
    //     if(resp.errno = "4101"){
    //         location.href = "/login.html";
    //     }else if(resp.errno == "0"){
    //         $("#user-name").val(resp.data.name)
    //     }
    // },"json");

// 进行用户名的更改操作
    $("#form-name").submit(function (e) {
        // 将表单的默认提交行为阻止掉
        e.preventDefault();
        var name = $("#user-name").val();
        if(!name){
            alert("请填写用户名");
            return;
        }
        $.ajax({
            url: "/api/v1.0/user/name",
            type: "PUT",
            data: JSON.stringify({name: name}),
            dataType: "json",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if(resp.errno == "0"){
                    $(".error-msg").hide();
                    showSuccessMsg();
                }else if("4001" == resp.errno){
                    $(".error-msg").show();
                }else if("4101" == resp.errno){
                    location.href = "/login.html";
                }
            }
        })
    })


})
