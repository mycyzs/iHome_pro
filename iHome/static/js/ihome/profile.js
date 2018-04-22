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
    // TODO: 在页面加载完毕向后端查询用户的信息
    //显示用户的信息

    $.get('/api/1.0/users',function (response) {

            if(response.reeno == '0'){

                 $('#user-avatar').attr('src', response.data.avatar_url);
                 $('#user-name').val(response.data.name);
            }else if(response.reeno = 4101){
                location.href = '/login.html'
            }else {
                alert(response.errmsg)
            }
    })


    // TODO: 管理上传用户头像表单的行为
    //禁用表单默认的提交行为
    $('#form-avatar').submit(function (event) {
        event.preventDefault();

            //对于file类型，模拟表单的提交，方便读取input里面的file值
        //m模拟表单提交就不用自己收集数据类，表单会默认收集数据
            $(this).ajaxSubmit({

            url:'/api/1.0/users/avatar',
            type:'post',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                //上传成功,直接显示在头像里
                if(response.reeno == '0'){
                    alert(response.errmsg)
                    $('#user-avatar').attr('src',response.data);
                }else if(response.reeno == '4101'){
                    location.href = '/longin.html'
                }else {
                    alert(response.errmsg)
                }
            }
        })

    })



    // TODO: 管理用户名修改的逻辑
    //禁用表单的默认提交行为
    $('#form-name').submit(function (event) {
        event.preventDefault()
        //校验参数
        var new_name = $('#user-name').val();
        if (!new_name) {
            alert('请输入用户名');
        }

        //封装参数
        var params = {
            'name':new_name
        }
        //发起put请求
        $.ajax({
            url:'/api/1.0/users/names',
            type:'put',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if(response.reeno == '0'){
                    //修改成功直接显示
                    showSuccessMsg()
                }else if(response.reeno = 4101){
                    location.href = 'login.html'

                }else {
                    alert(response.errmsg)
                }
            }
        })
    })

})

