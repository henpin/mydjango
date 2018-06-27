
function App(){
    var self = this;
    var canvas = null;
    var input_num = 0;
    var elem_holder = {}; // element-holder
    var elem_list = []; // element-holder2
    var tabber = [];
    var now_tabber = 0;
    var mode = "creation"; // 実行モード

    /* エントリーポイント*/
    this.init = function(){
        self.init_canvas();
        self.init_keyEvents();
        self.init_canvasEvents();
        self.init_domEvents();
        self.init_ajaxEvents();
        return self;
    }

    /* キャンバス初期化 */
    this.init_canvas = function(){
        // init canvas
        canvas = new fabric.Canvas('c');

        // set canvasSize
        canvas.setWidth($("#my-image").width());
        canvas.setHeight($("#my-image").height());

        // bg
        self.init_bg()
    }

    /* 背景初期化 */
    this.init_bg = function(){
        var img_path = $("#my-image").attr("src"); // ファイルパス
        canvas.setBackgroundImage(img_path, canvas.renderAll.bind(canvas));
    }

    /* キャンバスイベントの初期化*/
    this.init_canvasEvents = function(){
        // Events
        var startX = 0;
        var startY = 0;
        canvas.on('mouse:down', function(opt) {
            // 要素上なら無視
            if (opt.target && opt.target._objects){
                startX = 0;
                startY = 0;
            } else {
                startX = opt.pointer.x; // 保存
                startY = opt.pointer.y; // 保存
            }
        });

        canvas.on('mouse:up', function(opt){
            if ( mode != "creation"){ return; }
            var x = opt.pointer.x;
            var y = opt.pointer.y;

            if (x-startX<20 && y-startY<20){ return }
            if (!startX && !startY){ return }

            // rect
            var rect = new fabric.Rect({ 
                width: x -startX, height: y -startY,
                fill: '#3C8DBC', opacity: 0.2,
                });

            // text
            input_num += 1;
            var tmp_name = '入力'+input_num; // 一時テキスト
            var text = new fabric.IText(tmp_name, {
                width: x -startX, height: y -startY,
                fontSize:16, textAlign: "center"
            });
            text.metaName = tmp_name; // 一時名

            // group化して追加
            var group = new fabric.Group([rect,text],{
                left: startX, top: startY ,
                cornerSize: 6, hasRotatingPoint : false,
            });
            canvas.add(group)
            // 保存
            elem_holder[input_num] = group

            // フォームエリアに追加
            $("#form-area").append(
                '<div class="form-group col-sm-12 row">'
                    +'<div class="col-sm-12"><label class="control-label">入力欄'+input_num+'</label></div>'
                    +'<div class="col-sm-12 form-inline">'
                    +'<input type="text" class="form-control form-input col-sm-8" placeholder="入力項目名" data-target="'+input_num+'" style="width:300px;">'
                    +'<select class="form-control col-sm-4">'
                        +'<option value="サンプル1">フリー入力</option> <option value="サンプル2">数字</option> <option value="サンプル3">郵便番号</option>'
                        +'<option value="必須">必須</option>'
                    +'</select>'
                    +'</div>'
                +'</div>'
                );
            // イベントつける
            $(".form-input").change(function(){
                // 値を変える 
                elem_holder[$(this).attr("data-target")].item(1).set({ text : $(this).val() });
                // メタ名も一緒につける
                elem_holder[$(this).attr("data-target")].item(1).metaName = $(this).val();
                canvas.renderAll(); // レンダリング
            })
        });
    }

    /* フォームデータJSONを生成 */
    this.gen_dataJSON = function(){
        // JSONデータ
        var data = {};

        // Elemを簡易化
        if (Object.keys(elem_holder).length){ // フォームジェネレーション時
            Object.entries(elem_holder).forEach( (item,i) => {
                var elem = item[1];
                if (elem._objects){
                    var rect = elem._objects[0]
                    var text = elem._objects[1]
                    var metaName = text.metaName; // メタ名
                    // データに追加
                    data[metaName] = {
                        x : elem.left ,
                        y : elem.top,
                        width : rect.width,
                        height : rect.height,
                        text : text.text,
                        font : text.fontSize,
                        order : i, // 順序
                    };
                }
            })
        } else if (elem_list.length){ // フォーム入力時
            // データリストつくる
            elem_list.forEach( (elem,i) => {
                var metaName = elem.metaName; // メタ名
                // データ追加
                data[metaName] = {
                    x : elem.left ,
                    y : elem.top,
                    width : elem.width,
                    height : elem.height,
                    text : elem.text,
                    font : elem.fontSize,
                };
            })
        }

        // JSON化
        return JSON.stringify(data);
    }

    /* jsonデータからふぉーむつくる*/
    this.load_dataJson = function(_json){
        /* フォーム生成 */
        mode = "form"; // フォーム受付モード

        // jsonからオブジェクトデータ構築
        var json_data = JSON.parse(_json);
        // メタ名でくるくるしてBoxつくる
        Object.keys(json_data).forEach( metaName => {
            // データ
            var data = json_data[metaName];

            // 基礎データ抽出
            var settings = {
                left : data.x,
                top : data.y,
                width : data.width,
                height : data.height,
                text : data.text,
                hasControls : false,
                hasBorders : false,
            }

            // レクトつくる
            var rect = new fabric.Rect({ 
                fill: '#e8e8e8', opacity: 0.2,
                selectable: false,
                });
            // textつくる
            var text = new fabric.IText(data.text, {
                fontSize:16, textAlign: "center",
            });
            text.metaName = metaName; // メタ名ぶっこむ
            // 共通設定あてる
            rect.set(settings); text.set(settings);

            // エディタぶるディクトつくる
            self.add_editableRect(rect,text);
            // タバーにアッペンドする
            tabber.push(text);
        })
        
        canvas.renderAll();
    }

    /* DOMイベントの初期化 */
    this.init_domEvents = function(){
        // Nomal Events
        $('form').submit(function(e) { e.preventDefault();return false; });
        $("#json-btn").click( e => { 
            $("#json-out").val(JSON.stringify(canvas));
        })
        $("#load-json").click( e => { 
            var json_val = $("#json-in").val();
            // init
            canvas = new fabric.Canvas('c');
            canvas.loadFromJSON(json_val);
        })
        // My serialize
        $("#json-btn2").click( e => { 
            // jOSN生成
            var json = self.gen_dataJSON();
            // inputにぺタ
            $("#json-out2").val(json);
        })
        // My Jinput
        $("#load-json2").click( e => { 
            // 読む
            self.load_dataJson($("#json-in2").val());
        });
    }

    /* キーイベントアクティベーション */
    this.init_keyEvents = function(){
        $(window).keyup( e => {
            // タバー処理
            if (e.keyCode == 9 && tabber){
                now_tabber += 1;
                if (tabber.length <= now_tabber){
                    now_tabber = 0; // reset 
                }
                var elem = tabber[now_tabber];
                // フォーカス移動 
                elem.enterEditing();
                elem.selectAll();
            }

            // コピペ処理
            /*
            if (e.ctrlKey){
                if (e.keyCode == 67){
                    self.copy_elem(); // コピー
                } else if (e.keyCode == 86){
                    self.paste_elem(); // ペースト
                }
            }
            */
        });
    }

    /* 
    エディタぶるなRectをアッペンド
    新版。普通にやるver
    */
    this.add_editableRect = function(rect,text){
        /* 大きさ変更等不可 */
        text.hasControls = false;
        text.hasBorders = false;

        // ワンクリックで入力モード
        var _rect = rect; // for closure
        var _text = text; // for closure
        canvas.on("mouse:down",function(opt){
            if ( opt.target == _text || opt.target == _rect ){
                _text.enterEditing();
                _text.selectAll()
                //text.dirty = false;
                //canvas.renderAll()
            }
        })

        canvas.on("text:editing:exited", function(){
            _text.dirty = false;
            canvas.renderAll();
        })

        canvas.add(rect);
        canvas.add(text);

        // ElemListにほうりこむ
        elem_list.push(text);
    }

    /**
    * コピー関数
    */
    var _clipboard = null;
    this.copy_elem = function(){
        canvas.getActiveObject().clone(function(cloned) {
            _clipboard = cloned; // copy
            });
    }

    /* ペースト関数 */
    this.paste_elem = function(){
        // クローンする
        _clipboard.clone(function(clonedObj) {
            canvas.discardActiveObject();
            clonedObj.set({
                left: clonedObj.left + 10,
                top: clonedObj.top + 10,
                evented: true,
            });
            if (clonedObj.type === 'activeSelection') {
                // active selection needs a reference to the canvas.
                clonedObj.canvas = canvas;
                clonedObj.forEachObject(function(obj) {
                    canvas.add(obj);
                });
                // this should solve the unselectability
                clonedObj.setCoords();
            } else {
                canvas.add(clonedObj);
            }
            _clipboard.top += 10;
            _clipboard.left += 10;
            canvas.setActiveObject(clonedObj);
            canvas.requestRenderAll();
        });
    }

    /* Ajax関数 */
    var URL_FOR_FORM = "/pdf_form/form/save/";
    var URL_FOR_PDF = "/pdf_form/output/";
    var URL_FOR_COMMIT = "/pdf_form/commit/"
    this.init_ajaxEvents = function(){
        var uuid = $("#uuid").val(); // UUID抜く
        // フォーム生成ボタン
        $("#gen_form").click(function(){
            // 名前抜く
            var form_name = $("#form-name").val();
            // ふぉーむつくる
            var $form = $('<form/>', {'action': URL_FOR_FORM, 'method': 'post'});
            $form.append($('<input/>', {'type': 'hidden', 'name': "data", 'value': self.gen_dataJSON()}));
            $form.append($('<input/>', {'type': 'hidden', 'name': "uuid", 'value': uuid}));
            $form.append($('<input/>', {'type': 'hidden', 'name': "form_name", 'value': form_name}));
            $form.appendTo(document.body);
            $form.submit(); // サブミット
        });
        // PDF生成ボタン
        $("#gen_pdf").click(function(){
            // ふぉーむつくる
            var $form = $('<form/>', {'action': URL_FOR_PDF, 'method': 'post', "target" : "_blank"});
            $form.append($('<input/>', {'type': 'hidden', 'name': "data", 'value': self.gen_dataJSON()}));
            $form.append($('<input/>', {'type': 'hidden', 'name': "uuid", 'value': uuid}));
            $form.appendTo(document.body);
            $form.submit(); // サブミット
        });
        // 入力終了ボタン
        $("#commit").click(function(){
            // 名前抜く
            var form_name = $("#form-name").val();
            // ふぉーむつくる
            var $form = $('<form/>', {'action': URL_FOR_COMMIT, 'method': 'post'});
            $form.append($('<input/>', {'type': 'hidden', 'name': "data", 'value': self.gen_dataJSON()}));
            $form.append($('<input/>', {'type': 'hidden', 'name': "uuid", 'value': uuid}));
            $form.append($('<input/>', {'type': 'hidden', 'name': "form_name", 'value': form_name}));
            $form.appendTo(document.body);
            $form.submit(); // サブミット
        })
    }
}


// 読み込み時初期化
var app = null; // 公開
$(function(){ 
    app = new App();
    app.init();
    })

