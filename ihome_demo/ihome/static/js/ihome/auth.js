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
    $.get("/api/v1.0/user/auth", function (resp) {
        if(resp.errno == "4101"){
            location.href = "/login.html";
        }else if(resp.data.real_name && resp.data.id_card){
            $("#real-name").val(resp.data.real_name);
            $("#id-card").val(resp.data.id_card);
            // 为input框添加不可输入属性
            $("#real-name").prop("disables", true);
            $("#id-card").prop("disables", true);
            // 隐藏提交保存按钮
            $("#form-auth>input[type=submit]").hide()
        }
    });

    $("#form-auth").submit(function (e) {
        e.preventDefault();
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        if (real_name == "" ||  id_card == "") {
            $(".error-msg").show();
        }
        var req_data = {
            real_name: real_name,
            id_card: id_card
            };
        $.ajax({
            url: "/api/v1.0/user/auth",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(req_data),
            dataType: "json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if(resp.errno == "0"){
                    $(".error-msg").hide();
                    // 显示保存成功的提示信息
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                }
            }

        })
    });

})
