function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 获取得到全局唯一标识符
    imageCodeId = generateUUID();
    // 将得到的ID放入到url中
    var url = "api/v1.0/image_codes/" + imageCodeId;
    $(".image-code img").attr("src", url);

}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
     // 构造向后端请求的参数
    var req_data = {
        image_code: imageCode, // 图片验证码的值
        image_code_id: imageCodeId // 图片验证码的编号，（全局变量）
    };

    // 向后端发送请求
    $.get("/api/v1.0/sms_code/"+ mobile, req_data, function (resp) {
        // resp是后端返回的响应值，因为后端返回的是json字符串，
        // 所以ajax帮助我们把这个json字符串转换为js对象，resp就是转换后对象
        if (resp.errno == "0") {
            var num = 60;
            // 表示发送成功
            var timer = setInterval(function () {
                if (num >= 1) {
                    // 修改倒计时文本
                    $(".phonecode-a").html(num + "秒");
                    num -= 1;
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer);
                }
            }, 1000, 60)
        } else {
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }
    });
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        // 构造向前端发送的json数据
        var rep_data = {
            sms_code : phoneCode,
            mobile : mobile,
            password : passwd,
            password2 : passwd2,
        };
         var rep_json = JSON.stringify(rep_data);
        $.ajax({
            url : "/api/v1.0/register",
            type : "post",
            contentType : "application/json",
            data : rep_json,
            dataType : "json",
            headers :{
              "X-CSRFToken" : getCookie("csrf_token")
            },
            success : function (resp) {
                if (resp.errno == "0"){
                    location.href = "/index.html";
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    });
})