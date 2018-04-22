function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 查询用户的实名认证信息
    //刷新页面时主动加载用户实名认证的信息
    $.get('/api/1.0/users/info',function (response) {
        if(response.reeno == '0'){
            //显示数据
            //如果用户已经实名认证了，显示并且不可更改了
            if(response.data.real_name && response.data.id_card){
                 $('#real-name').val(response.data.real_name)
                $('#id-card').val(response.data.id_card)

                //隐藏输入框，并且固定
                $('#real-name').attr('disabled', true);
                $('#id-card').attr('disabled', true);
                $('.btn-success').hide();
            }else if(response.reeno == '4101'){
                location.href = 'login.html'
            }else {
                alert(response.errmsg)
            }

        }
    })


    // TODO: 管理实名信息表单的提交行为
    $('#form-auth').submit(function (event) {
        event.preventDefault()  //禁用表单的默认提交行为

        //前端校验
        var real_name = $('#real-name').val()
        var id_card = $('#id-card').val()

        if (!real_name) {
            alert('请输入真实姓名')
        }
        if (!id_card) {
            alert('请输入身份证号码')
        }

        //封装参数
        var params = {
            'real_name':real_name,
            'id_card':id_card
        }

        //发起post请求,如果是图片的获取就用表单默认的提交行为
        $.ajax({
            url:'/api/1.0/users/auth',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if(response.reeno == '0'){
                    alert('实名认证通过')
                }else if(response.reeno == '4101'){
                    location.href = 'login.html'
                }else {
                    alert(response.errmsg)
                }
            }
        })
    })

})