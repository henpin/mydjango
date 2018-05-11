/**
* チャットＪＳ
*
*/
// ワークスペース
var WS_ID = {{ WS_ID }};

// Ajax URL
var CONV_URL = "/djatson/kaminaga/conversation/"; // カンバゼーションAjaxエンドポイント

/**
* ワトソン呼び出し関数
* 
* AJAX使うのでちょっとしゃれたことやる
* 一種のオブザーバーパターん
* 規約はupdate関数
*/
function call_watson(question,listener){
    /* でーた構築*/
    var data = {
        ws_id : WS_ID,
        input : question
    };

    /* データの送信 */
    $.ajax({
      url: CONV_URL, 
      type: "POST",
      dataType: 'json',
      data: data
    })
    .done(function(data){
        /* 呼び出しもとに通知*/
        str = data.response.replace(/(\r?\n)+|\n+/g,"<BR>").replace(/(<BR>)+|(<br>)+/g,"<BR>")
        var joined = "以下を参照してください<BR>";
        var add2joined = function(str){ joined += ( "<li>" +str +"</li>" ); }
        /* マッチングした候補ごとに処理 */
        str.split("以下を参照してください<BR>").forEach(function(s){
            if (s){
                //joined += "以下を参照してください<BR>" ;
                if (s.startsWith("<")){ // tagから始まるならiframe化
                    s = s.replace(/<BR>/g,"").replace(/\&/g,"&amp;").replace(/\"/g,"&quot;")
                    joined += '<iframe style="width:100%;height:300px;" srcdoc="' + s +'"></iframe>' ;
                } else { // 普通に追加
                    joined += s;
                }
            }
        })

        listener.update(AutoLink(joined));
        console.log(data);
    })
    .fail(function(data,e){
        /* 呼び出しもとに通知*/
        listener.update("通信に失敗したようです");
        console.log(data)
        console.log(e)
    })

    console.log(data);
}

/* 拾ってきた文字列Aタグ化関数*/
function AutoLink(str) {
    var regexp_url = /((h?)(ttps?:\/\/[a-zA-Z0-9.\-_@:/~?%&;=+#',()*!]+))/g; // ']))/;
    var regexp_makeLink = function(all, url, h, href) {
        return '<a href="h' + href + '" target="_blank">' + url + '</a>';
    }
 
    return str.replace(regexp_url, regexp_makeLink);
}


/**
* DjangoでAjaxできるようにする
*/
init_ajax = function(){
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
$(function(){ init_ajax(); })
