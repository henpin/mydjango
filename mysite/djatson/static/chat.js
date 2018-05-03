/**
* チャットＪＳ
*
*/
var WS_ID = {{ WS_ID }};
var INITIALIZED = {{ INITIALIZED }};

/**
* ワトソン呼び出し関数
* 
* AJAX使うのでちょっとしゃれたことやる
* 一種のオブザーバーパターん
* 規約はupdate関数
*/
function call_watson(question,listener){
    if (!INITIALIZED){
        listener.update("watsonの初期化が完了していないようです")
    } else {
        listener.update(question+"に対する応答")
        listener.update("工事中")
    }
}
