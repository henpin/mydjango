
/**
* 汎用のバリデーション設定JS
*/

/*
* 適当クラス
*/
function Setting(){
    var self = this

    /* 初期化関数 */
    self.init = function(){
       self.init_events(); // イベントまわり設定
       self.init_jp_validation(); // 日本語拡張
       self.init_error_msg(); // エラーメッセージ設定
    }

    /**
    * イベント設定
    */
    self.init_events = function(){
        // jQueryバリデーションはonChange拾わないので、拾うようにしちゃう
        $("input").on("change",function(){
            console.log("onchange validation...")
            $(this).valid();
        });
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

}

// 読み込み時初期化
$(function(){ new Setting().init(); })
