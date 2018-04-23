
/**
* 悪い神長志向JS
* ゴリラ志向
*/

// 置き換え用グローバルオブジェクト
var RULES_OBJ = {{ RULES_OBJ }}; // { input_name : { validation_type : val } }
var TARGET_FORM_NAME = "{{ FORM_NAME }}"; // バリデーション対象フォーム名
//var ERROR_DIV_TEMPLATE = "<div class='popover popover-validation' role='tooltip'><div class='arrow'></div><h3 class='popover-title'></h3><div class='popover-content'></div></div>";
var LOG_URL = "/djangolla/kaminaga/logging/"; // ログAjaxエンドポイント

/* アプリケーションクラス */
function App(){
    var self = this;

    /* 初期化関数 */
    self.init = function(){
       self.init_validation(); // バリデーション初期化
       self.set_autoSync(); // ロギング設定
       self.init_ajax(); // DjangoでAjaxする呪文
    }

    /* バリデーション初期化 */
    self.init_validation = function(){
        // バリデーション定義
        $("form[name='NAME']".replace("NAME",TARGET_FORM_NAME)).validate({
            rules : RULES_OBJ, // ルール定義
            showErrors: function(errorMap, errorList) { // ゴリラ
            // validationに引っかからなかった要素はpopover非表示にする
            $.each(this.successList, function(index, value) {
                $(value).popover('hide');
                });

            // validationに引っかかった要素はpopover表示する
            $.each(errorList, function(index, value) {
                var _popover = $(value.element).popover({
                    trigger: 'manual',
                    placement: 'bottom',
                    content: value.message
                    //template: ERROR_DIV_TEMPLATE
                });
                _popover.data('bs.popover').config.content = value.message; // popover要素のテキストを更新する
                $(value.element).popover('show');
                setTimeout(function(){ _popover.popover("hide") },8000)
                });
            }
        });
    }

    /**
    * 自動送信定義
    */
    self.set_autoSync = function(){
        // フォーム化の全inputでイーチ
        $("form[name='NAME']".replace("NAME",TARGET_FORM_NAME)).find("input").each(function(){
            // 送信関数
            var self = this;
            function doSend(){
                // データ取得
                data = {
                    input_name : $(self).attr("name"),
                    input_value : $(self).val(),
                    uuid : $("#uuid").val()
                }

                /* データの送信 */
                $.ajax({
                  url: LOG_URL, 
                  type: "POST",
                  data: data
                })
                .done(function(data){console.log("log data send");})
                console.log(data);
            }

            // on changeにバインド
            //$(this).change(doSend).keyup(function(e){ if(e.keyCode == 13 /* Enter-key */ ){doSend();} });
            $(this).change(doSend).keyup(doSend);
        });
    }


    /**
    * DjangoでAjaxできるようにする
    */
    self.init_ajax = function(){
        $(document).ajaxSend(function(event, xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = $.trim(cookies[i]);
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            function sameOrigin(url) {
                var host = document.location.host;
                var protocol = document.location.protocol;
                var sr_origin = '//' + host;
                var origin = protocol + sr_origin;
                return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                    !(/^(\/\/|http:|https:).*/.test(url));
            }

            function safeMethod(method) {
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }

            if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        });
    }

}

// 読み込み時起動
$(function(){ new App().init(); })
