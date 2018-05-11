var me = {};
me.avatar = "https://lh6.googleusercontent.com/-lr2nyjhhjXw/AAAAAAAAAAI/AAAAAAAARmE/MdtfUmC0M4s/photo.jpg?sz=48";

var you = {};
you.avatar = "https://a11.t26.net/taringa/avatares/9/1/2/F/7/8/Demon_King1/48x48_5C5.jpg";

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}            

//-- No use time. It is a javaScript effect.
function insertChat(who, text, time){
    if (time === undefined){
        time = 0;
    }
    var control = "";
    var date = formatAMPM(new Date());
    
    if (who == "me"){
        control = '<li style="width:100%">' +
                        '<div class="msj macro">' +
                        '<div class="avatar"><img class="img-circle" style="width:100%;" src="'+ me.avatar +'" /></div>' +
                            '<div class="text text-l">' +
                                '<p>'+ text +'</p>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '</div>' +
                    '</li>';                    
    }else{
        control = '<li style="width:100%;">' +
                        '<div class="msj-rta macro">' +
                            '<div class="text text-r">' +
                                '<div>'+text+'</div>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '<div class="avatar" style="padding:0px 0px 0px 10px !important"><img class="img-circle" style="width:100%;" src="'+you.avatar+'" /></div>' +                                
                  '</li>';
    }
    setTimeout(
        function(){                        
            $("ul").append(control).scrollTop($("ul").prop('scrollHeight'));
        }, time);

}

function resetChat(){
    $("ul").empty();
}

/* レシーバークラス */
function Receiver(){
    /* 規約 */
    this.update = function(string){
        return insertChat("you",string);
    }
}
var RECEIVER = new Receiver();

function init(){
    /* テキスト入力欄 */
    $(".mytext").on("keyup", function(e){
        if (e.which == 13){ /* エンターキーで送信 */
            var text = $(this).val();
            if (text !== ""){
                insertChat("me", text); // 表示欄に追加
                $(this).val(''); // テキスト欄をきれいに

                // 送信
                call_watson(text,RECEIVER);
            }
        }
    });
    $('body > div > div > div:nth-child(2) > span').click(function(){
        $(".mytext").trigger({type: 'keyup', which: 13, keyCode: 13});
    })

    //-- Clear Chat
    resetChat();

    //-- Print Messages
    insertChat("you", "こんにちはkaminagaさん", 1000);
    insertChat("me", "こんにちは", 2000);
    insertChat("you", "入力されたURLからスクレイピングして知識を蓄えました", 3000);
    insertChat("you", "質問をどうぞ", 4000);
}

$(function(){init()})
