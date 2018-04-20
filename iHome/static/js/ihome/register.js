function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}
var uuid = "";
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {

    // 上传本次图片验证码对应的uuid:唯一区分这个图片验证码是从那个浏览器发送过来的
     uuid = generateUUID();   //函数内部改变全局变量不可以用var

    // 生成图片验证码对应的<img>标签的url
    var url = '/api/1.0/image_code?uuid=' + uuid;

    // 将url的值赋值给<img>标签的属性
    $('.image-code>img').attr('src', url);
}

function sendSMSCode() {


    // 校验参数，保证输入框有数据填写
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

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码

    //获取参数
    var params = {
        'mobile':mobile,
        'ImageCode':imageCode,
        'uuid':uuid
    };


    //点击获取短信验证码，发起post请求到后台进行数据的校验
    $.ajax({
        url: '/api/1.0/sms_code',
        type: 'post',
        data: JSON.stringify(params),
        contentType: 'application/json',
        headers: {'X-CSRFToken': getCookie('csrf_token')},
        success: function (response) {
            if (response.errno == '0') {
                //发送成功，时间倒计时60s
                var num = 60;
                var t = setInterval(function () {
                    if (num == 0) {
                        // 倒计时完成,清除定时器
                        clearInterval(t);         // 重新生成验证码
                        generateImageCode();
                        // 重置内容
                        $(".phonecode-a").html('获取验证码');
                        // 重新添加点击事件
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    } else {
                        // 正在倒计时，显示秒数
                        $(".phonecode-a").html(num + '秒');
                    }

                    num = num - 1;
                }, 1000);

            } else {
                // 重新添加点击事件
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                // 重新生成验证码
                generateImageCode();
                // 弹出错误消息
                alert(response.errmsg);
            }

        }


    })


}

$(document).ready(function () {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function () {
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function () {
        $("#phone-code-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function () {
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
})
