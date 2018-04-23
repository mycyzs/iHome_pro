function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    //利用Art_template渲染html，前端在html里面用到script
    //得到html，直接在标签渲染据可以了
    $.get('/api/1.0/areas', function (response) {
        if (response.reeno == '0') {
            //取到数据，渲染
            var html = template('areas-tmpl', {'areas': response.data})
            //将生成的html赋值给某个标签
            $('#area-id').html(html)
        } else {
            alert(response.errmsg)
        }
    })


    // TODO: 处理房屋基本信息提交的表单数据
    //禁用表单的提交行为
    $('#form-house-info').submit(function (event) {
        event.preventDefault()
        //定义一个字典，把input标签的name和value放进字典，组成键值对
        var params = {};
        //一个个标签收集太多了，用序列化将表单中带有name和input的标签生成字典对象
        $(this).serializeArray().map(function (obj) {
            params[obj.name] = obj.value
             });
            //对于配套设施，name都是facility，把value组成一个列表，
            //facility：[1,2,3,5],这种形式，覆盖前面生成的facility
            var facility_list = [];
            //获取所有选中的checkbox对象,name必须是facility
            $(':checkbox:checked[name=facility]').each(function (i, elem) {
                facility_list[i] = elem.value
            });
            //加入params字典，覆盖之前的
            params['facility'] = facility_list;

            //发起ajax请求
            $.ajax({
                url: '/api/1.0/houses',
                type: 'post',
                data: JSON.stringify(params),
                contentType: 'application/json',
                headers: {'X-CSRFToken': getCookie('csrf_token')},

                success: function (response) {
                    if (response.reeno == '0') {

                        //发布成功隐藏这些字段，并且打开上传房屋图片的表单
                        $('#form-house-info').hide();
                        $('#form-house-image').show();
                        // 将发布成功的house_id渲染到界面上
                        $('#house-id').val(response.data.house_id);
                    }
                }
            })



    })

    // TODO: 处理图片表单的数据
    //上传房子的图片
    $('#form-house-image').submit(function (event) {
        event.preventDefault()

        //因为这里是图片的上传，图片数据不好拿到，所以模拟表单的提交行为
        $(this).ajaxSubmit({
            url: '/api/1.0/house/image',
            type: 'post',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (response) {
                if (response.reeno == '0') {
                    alert(response.errmsg)
                    $('.house-image-cons').append('<img src="' + response.data + '">')
                } else if (response.reeno == '4101') {
                    location.href = 'login.html'
                } else {
                    alert(response.errmsg)
                }
            }
        })
    })

})