
/**
* 拾いもの
* Copyright © 2013 pistatium Distributed under the MIT License.
*/

/* JSON */
JSONDATA = '{{ JSON }}';


/* main */
function show_json(jsonStr){
    // 生成先セレクタ
    var selector = "#result";
    // レンダリング病がいき
    var result = dump(jsonStr);

    // 描画処理
    $(selector).hide();
    $(selector).html(result); // 描画
    $(selector).show("fast");
    setListner();
}

/* ぱっディングをトリムする*/
var trimPadding = function(jsonp){
    var match = null;
    var json_obj = '';
    var json_array = '';
    
    match = jsonp.match(/\{[\s\S]*\}/);
    if(match){
        var json_obj = match.toString();
    }
    
    match = jsonp.match(/\[[\s\S]*\]/);
    if(match){
        var json_array = match.toString()
    }
    
    if (json_array.length > json_obj.length) {
        return json_array;
    }
    console.log(json_obj)
    return json_obj;
}

/* jsonをパーすする*/
var parseJSON = function(json){
    if (!json){
        alert("jsonが空のようです")
        return;
    }
    try{
        var obj = JSON.parse(json);
    } catch(e){
        alert("[ERROR] Wrong JSON Format\n\n" + e);
        console.debug(json);
    }

    return obj;
}

/* それらしい形式にダンプする*/
var dump = function(json){
    json = trimPadding(json);
    var obj = parseJSON(json);
    var formatted_json = JSON.stringify(obj, null, 4);
    console.log(formatted_json);
    $("#raw_json").val(formatted_json);
    return makeHtml(obj);
}


/* htmlつくる */
var makeHtml = function(obj){
    return "<span class='key'>ROOT</span>" + _make(obj, "");
}

/* htmlつくるロジック */
var _make = function(obj, nest){
    if (obj == null) {
        return "<span class='val no_val'>(null)</span>"
             + "<span class='place'>"
             + nest 
             + "</span>"
             + "<br>";
        
    } else if (typeof obj == 'object') {
        var tmp ="<span class='array'>(array)<br></span><div class='indent'>"
        for(o in obj){ 
            tmp += "<span class='key'>"
                 + o
                 + "</span>:" 
                 + _make(obj[o], nest + "['" + o + "']");
        }
        return tmp + "</div>";
        
    } else {
        return "<span class='val'>"
             + _escape(obj)
             + "</span>"
             + '<input class="place" size=100 value="data'
             + nest
             + '" onclick="this.select();" />'
             + "<br>";
    }
}

/* クリックリスナーつける */
var setListner = function(){
    $(".key").click(function(){
        $(this).next(".array").next(".indent").toggle("fast");
    });
    $(".array").click(function(){
        $(this).next(".indent").toggle("fast");
    });
    $('.place').click(function(){
        //alert(this.innerText);
    });

}

/* 文字のエスケープ処理*/
var _escape = function(ch) {
    if(typeof ch !== 'string')return ch;
    ch = ch.replace(/&/g,"&amp;") ;
    ch = ch.replace(/"/g,"&quot;") ;
    ch = ch.replace(/'/g,"&#039;") ;
    ch = ch.replace(/</g,"&lt;") ;
    ch = ch.replace(/>/g,"&gt;") ;
    return ch ;
}

// 起動時ジッコウ
$(function(){ new show_json(JSONDATA); })

