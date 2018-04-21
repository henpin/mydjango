
/**
* リプレイJS
*
* 悪い神長志向JS
* ゴリラ志向
*/

// 置き換え用グローバルオブジェクト
var RULES_OBJ = {{ RULES_OBJ }}; // { input_name : { validation_type : val } }
var TARGET_FORM_NAME = "{{ FORM_NAME }}"; // バリデーション対象フォーム名
//var ERROR_DIV_TEMPLATE = "<div class='popover popover-validation' role='tooltip'><div class='arrow'></div><h3 class='popover-title'></h3><div class='popover-content'></div></div>";
// var LOG_URL = "/djangolla/kaminaga/logging/"; // ログAjaxエンドポイント
var REPLAY_DATA = {{ REPLAY_DATA }};

/* アプリケーションクラス */
function App(){
    var self = this;

    /* 初期化関数 */
    self.init = function(){
       self.init_validation(); // バリデーション初期化
       //self.init_replay(); // リプレイ初期化
       self.do_replay();
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

    /* りぷれいする*/
    self.do_replay = function(){
        alert("リプレイを開始します");

        // リプレイデータごとにsetTimeoutして入力予約
        REPLAY_DATA.forEach(function(data){
            // 情報取得
            var name = "input[name='" +data.input_name +"']" // 対象input名
            var val = data.input_value; // 値
            var time = data.time *1000; // 時間(ちょっと引き伸ばす)

            console.log(name +":" +val +":" +time)

            // setTimeoutする
            setTimeout(function(){
                $("input").css("color","black");
                // 値変えて色変えてchangeイベント起こす
                $(name).val(val) .css("color","red") .change();
                }, time);
        });
    }

}

// 読み込み時起動
$(function(){ new App().init(); })
