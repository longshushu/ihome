function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    $.get("/api/v1.0/area", function (resp) {
        if(resp.errno == "0"){
            var areas = resp.data
            var html = template("areas-tmpl",{areas: areas} );
            $("#area-id").html(html);
        }else{
            alert(resp.errmsg);
        }
    }, "json");
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
         // 处理表单数据
        var data = {};
        $("#form-house-info").serializeArray().map(function (x) {
            data[x.name]=x.value
        });
        // 收集设置id信息
        var facility =[]
        $(":checked[name=facility]").each(function (index) {
            facility[index] = $(this).val()
        });
        data[facility] = facility;
        // 向后端发送请求
        $.ajax({
            url: "/api/v1.0/user/info",
            type: "post",
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if(resp.errno == "4101"){
                    location.href = "/login.html"
                }else if(resp.errno == "0"){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id);
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    });
})