
/**
* 悪い神長志向JS
* ゴリラ志向
*/

// 置き換え用グローバルオブジェクト
var RULES_OBJ = {{ RULES_OBJ }}; // { input_name : { validation_type : val } }
var TARGET_FORM_NAME = "{{ FORM_NAME }}";
var ERROR_DIV_TEMPLATE = "<div class='popover popover-validation' role='tooltip'><div class='arrow'></div><h3 class='popover-title'></h3><div class='popover-content'></div></div>";
var LOG_URL = "/djangolla/kaminaga/logging/"

/* アプリケーションクラス */
function App(){
    var self = this;

    /* 初期化関数 */
    self.init = function(){
       self.init_jp_validation();
       self.init_error_msg();
       self.init_validation();
       self.set_autoSync();
       self.init_ajax();
    }

    /**
    * 日本語用バリデーション追加。拾ってきた
    */
    self.init_jp_validation = function(){
        //全角ひらがな･カタカナのみ
        jQuery.validator.addMethod("kana", function(value, element) {
            return this.optional(element) || /^([ァ-ヶーぁ-ん]+)$/.test(value);
            }, "全角ひらがな･カタカナを入力してください"
        );

        //全角ひらがなのみ
        jQuery.validator.addMethod("hiragana", function(value, element) {
            return this.optional(element) || /^([ぁ-ん]+)$/.test(value);
            }, "全角ひらがなを入力してください"
        );

        //全角カタカナのみ
        jQuery.validator.addMethod("katakana", function(value, element) {
            return this.optional(element) || /^([ァ-ヶー]+)$/.test(value);
            }, "全角カタカナを入力してください"
        );

        //半角カタカナのみ
        jQuery.validator.addMethod("hankana", function(value, element) {
            return this.optional(element) || /^([ｧ-ﾝﾞﾟ]+)$/.test(value);
            }, "半角カタカナを入力してください"
        );

        //半角アルファベット（大文字･小文字）のみ
        jQuery.validator.addMethod("alphabet", function(value, element) {
            return this.optional(element) || /^([a-zA-z\s]+)$/.test(value);
            }, "半角英字を入力してください"
        );

        //半角アルファベット（大文字･小文字）もしくは数字のみ
        jQuery.validator.addMethod("alphanum", function(value, element) {
            return this.optional(element) || /^([a-zA-Z0-9]+)$/.test(value);
            }, "半角英数字を入力してください"
        );

        //郵便番号（例:012-3456）
        jQuery.validator.addMethod("postnum", function(value, element) {
            return this.optional(element) || /^\d{3}\-\d{4}$/.test(value);
            }, "郵便番号を入力してください（例:123-4567）"
        );

        //携帯番号（例:010-2345-6789）
        jQuery.validator.addMethod("mobilenum", function(value, element) {
            return this.optional(element) || /^0\d0-\d{4}-\d{4}$/.test(value);
            }, "携帯番号を入力してください（例:010-2345-6789）"
        );

        //電話番号（例:012-345-6789）
        jQuery.validator.addMethod("telnum", function(value, element) {
            return this.optional(element) || /^[0-9-]{12}$/.test(value);
            }, "電話番号を入力してください（例:012-345-6789）"
        );
    }

    /**
    * エラーメッセージ初期化
    * from ゴリラ
    */
    self.init_error_msg = function(){
        // エラーメッセージの定義
        $.extend( $.validator.messages,{
            required: "{1}を入力してください。",
            remote: "このフィールドを修正してください。",
            email: "有効なEメールアドレスを入力してください。",
            mail: "{1}を入力してください。",
            url: "有効なURLを入力してください。",
            date: "有効な日付を入力してください。",
            dateISO: "有効な日付（ISO）を入力してください。",
            number: "有効な数字を入力してください。",
            digits: "数字のみを入力してください。",
            creditcard: "有効なクレジットカード番号を入力してください。",
            equalTo: "同じ値をもう一度入力してください。",
            extension: "有効な拡張子を含む値を入力してください。",
            maxlength: $.validator.format( "{0} 文字以内で入力してください。" ),
            minlength: $.validator.format( "{0} 文字以上で入力してください。" ),
            rangelength: $.validator.format( "{0} 文字から {1} 文字までの値を入力してください。" ),
            range: $.validator.format( "{0} から {1} までの値を入力してください。" ),
            max: $.validator.format( "{0} 以下の値を入力してください。" ),
            min: $.validator.format( "{0} 以上の値を入力してください。" )
        });
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
                setTimeout(function(){ _popover.popover("hide") },5000)
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
            $(this).change(doSend).keyup(function(e){ if(e.keyCode == 13 /* Enter-key */ ){doSend();} });
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
