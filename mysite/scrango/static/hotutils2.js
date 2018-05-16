
/**
* HOTユーティリティ
*
* このモジュールは以下の部分に分かれる
*
* ・汎用初期化部分
*   initializeHOTを始点とする共通インターフェイス追加機構。
*   HOTオブジェクトそのものを修飾し、より高度な機能インターフェイスを付与する
*
* ・通信部分
*   サーバーサイドHOTUtilsに適合した送受信機構を備える機能インターフェイスを付与する
*   これもHOTオブジェクトに機能インターフェイスを与える形をとる
*
* ・推論機能部分
*   情報ネットワークの概念を基盤とした、ネットワークの制約/復元機構の利用と
*   そのための利用インターフェイスを与える
*
*/


/**
* HOT汎用初期化関数
* 初期化対象DIVIDとオプションのHOT-settingsオブジェクトをとる
*
* HOTオブジェクトを取得するエントリーポイント
*/
function initializeHOT(divId,optionalSettings){
	// HOT生成対象DIV
	var targetDiv = document.getElementById(divId);
    var japaneseKeycodeList = [28, 29, 241, 242, 243, 244];

	/* 汎用基本設定 */
	var settings = {
		//height: 500, // 大体強制しておいたほうがいい
		//width: 1000,
        stretchH: 'all',
		startRows: 50, //初期表示行数
        startCols: 50,
        rowHeights: 34,
        columnHeaderHeight: 28,
        colHeaders : ["A","B","C","D"],
		//columnSorting: true, //列ソート可否
		//sortIndicator: true, //ソート列に三角印を表示
		minSpareRows: 2, //最下行に空白行を1行
        minRows: 2,
		fillHandle: true, //possible values: true, false, "horizontal", "vertical"
		enterMoves: { row: 1, col: 0 }, // エンターによる移動
		rowHeaders: true, // 行ヘッダ
		rowHeaderWidth: 20,
		wordWrap :true, // 行畳み込み
        manualColumnFreeze:true, // カラムの動きの設定
        manualColumnResize:true,
        manualRowResize:true,
        currentRowClassName: 'currentRow', // 行ハイライト
        currentColClassName: 'currentCol',
        mergeCells: true, // セルマージ
        comments: true,
        customBorders : true,
        //日本語入力関連キーを無視
        beforeKeyDown: function(e) {
          if (japaneseKeycodeList.indexOf(e.keyCode) != -1) {
            e.isImmediatePropagationEnabled = false;
            e.isImmediatePropagationStopped = function(){ return true; }
          }
        },
		//右クリックメニューのカスタマイズ
		contextMenu: {
			items: {
			row_above: { name: '上に行を挿入' },
			row_below: { name: '下に行を挿入' },
			col_left: { name: '左に列を挿入' },
			col_right: { name: '右に列を挿入' },
			remove_row: { name: 'この行を削除' },
			remove_col: { name: 'この列を削除' },
			undo: { name: '元に戻す' },
			redo: { name: 'やり直す' },
          //freeze_column: { name : 'カラム固定' },
          //unfreeze_column: { name : '固定解除' }
		    }
	    },
        modifyColWidth: function(width, col){ // 最大幅
            if( width > 350 ){ return 350; }
            },
        search: true,  //検索有効
        // enterMoves: { row: 1, col: -100 },
        // renderAllRows: true // 全行描画:重い
	};

	/* オプショナル設定のアップデート*/
	if ( optionalSettings ){
    optionalSettings = ( optionalSettings instanceof Function ) ? optionalSettings(HOT) : optionalSettings; // 関数名なら実行
    Object.assign(settings,optionalSettings); //アサイン
  }

  /* HOTオブジェクトの生成 */
  var HOT = new Handsontable(targetDiv, settings);

  /* なんかSpace入力時バグがおきるのでPreventDefault*/
  HOT.addHook("afterKeyDown",function(e){e.keyCode == 32 && e.preventDefault();});

  /* 10秒に1回自動リローディングを行う。ぐちゃぐちゃにならないようにね。*/
  setInterval(function(){ HOT.render(); console.log("Rerendering HOT...") },10000);

  return HOT;
}


/**
* HOT一般装飾クラス
*
* HOTオブジェクトに汎用のAPIを付与するクラス
+ 早い話がインスタンス束縛済みのユーティリティメソッドの束縛をする
*/
function HOTModifier(){
  this.hot = null;
  var self = this;
  /**
  * 初期化関数
  */
  this.init = function(hot){
    self.hot = hot;
    return self;
  }

  /**
  * 全基本API設定インターフェイス
  */
  this.add_commonAPI = function(hot){
    hot = self.hot || hot;
    /* コントロール主導のショートカットAPI */
    self.add_HOTCTRLShortcutAPI(hot);
    /* ダブルクリックAPI */
    self.add_HOTDblClickAPI(hot)
    /* セルマージAPI */
    self.add_HOTMergeAPI(hot);
    /* アライメントアクセスAPI */
    self.add_HOTAlignmentAPI(hot);
    /* DOMオブジェクトイベントコネクションAPIの追加*/
    self.add_HOTDomConnectionAPI(hot);
    /* ボーダー定義API */
    self.add_HOTBorderAPI(hot);
    /* リサイズAPI */
    self.add_HOTResizeAPI(hot);
    /* コモンAPI*/
    self.add_HOTCommonAPI(hot);
    /* インターバルAPI */
    self.add_HOTIntervalAPI(hot);
    /* セルプロパティAPI */
    self.add_HOTCellPropAPI(hot);
    /* コンテキストメニューAPI */
    self.add_HOTContextMenuAPI(hot)

    return self;
  }

  /**
  * コモンAPI
  * 最も汎用のユーティリティ関数を付与
  */
  this.add_HOTCommonAPI = function(HOT){
    /* 単純な空行の探索メソッド */
    HOT.findLastEmptyRow = function(){
      for (i=0;i<=1000;i++){ // 1000行見る
        if ( HOT.isEmptyRow(i) ){ return i; } ;
      }
      throw "空行検索条件を超えました"
    }

    /* 選択情報保持 */
    HOT.prevSelected = [0,0,0,0]; /*{ row:row, col:col, endRow:endRow, endCol:endCol };*/
    HOT.addHook("afterSelection",function(row,col,endRow,endCol){ HOT.prevSelected = [row,col,endRow,endCol]; });
    HOT.getPrevSelected = function(){ return HOT.prevSelected; }

    /* 選択情報取得 */
    HOT.getSelectedPos = function(){
      var selected = HOT.getSelected();
      if ( !selected ){
        return HOT.getPrevSelected();
      }
      return selected;
    }

    /* 座標Row-Range取得 */
    HOT.getRowRange = function(){
      var last_row = HOT.countRows();
      return Array.from({length:last_row}, (v,k) => k);
    }

    /* 座標Col-Range取得 */
    HOT.getColRange = function(){
      var last_col = HOT.countCols();
      return Array.from({length:last_col}, (v,k) => k);
    }

  }

  /**
  * ダブルクリックAPI
  *
  * ダブルクリックイベントを追加
  */
  this.add_HOTDblClickAPI = function(HOT){
    /* ダブルクリック状態保存名前空間 */
    var nameSpace = {
      clickTime : new Date().getTime(),
      pos : {row :0,col:0}
      };
    /* ダブルクリックイベントの追加 */
    Handsontable.hooks.add("afterOnCellMouseDown",function(e,pos){
      var time = new Date().getTime();
      if ( time != nameSpace.clickTime && time - nameSpace.clickTime <= 500 && pos.row == nameSpace.pos.row && pos.col == nameSpace.pos.col ) {
        Handsontable.hooks.run(HOT,"dblClick",pos.row,pos.col);
      }
      nameSpace.clickTime = time;
      nameSpace.pos = pos;
    },HOT);
  }

  /**
  * HOTにショートカット定義APIを定義
  *
  * コマンドショートカットを簡単に付与,操作できるようになる
  */
  this.add_HOTCTRLShortcutAPI = function(HOT){
    var shortCuts = new Map();
    HOT.addHook("beforeKeyDown",function(e){
      if ( e.ctrlKey && shortCuts.has(e.code)){
          shortCuts.get(e.code)(HOT,e);
          e.preventDefault(); // デフォルト処理の中止
      }
    });
    // ショートカット追加関数の追加
    HOT.addCTRLShortcut = function(keyName,hookFunc){
      shortCuts.set(keyName,hookFunc);
    };
  };

  /**
  * HOTリサイズ定義API
  *
  * 自動リサイズ用ユーティリティ関数の付与
  */
  this.add_HOTResizeAPI = function(HOT){
    /* コンテナ取得 */
    var getContainer = function(selector){
      selector = selector || ".HOT-container";
      var container = $(HOT.rootElement).closest(selector);
      if ( ! container.length ){
        return $(selector);
      }
      return container;
    }
    HOT.getContainer = getContainer;
    /* サイジング例外オブジェクトの取得 */
    var getExclusive = function(container,selector){
      if ( ! selector ){
        selector = ".HOT-exclusive";
        return container.find(selector);
      } else {
        return $(selector);
      }
    }

    /* コンテナ基準のサイズ調整 */
    HOT.setAdjuster = function($container,$exclusive,adjustment){
      adjustment = adjustment || 0;
      /* サイズの基準となるコンテナの取得 */
      var container = getContainer($container);
      /* サイズ例外セレクタ */
      var exclusive = getExclusive(container,$exclusive);

      /* サイズ調整関数 */
      var adjuster = function(){
        /* height */
        var baseHeight = container.innerHeight();
        var exclusive_height = 0;
        exclusive.each(function(){
          exclusive_height += $(this).outerHeight();
          });

        var height = baseHeight -exclusive_height +adjustment;
        if (height >= 1500){ height = 1000; }

        /* width */
        var baseWidth = container.innerWidth();

        /* update */
        HOT.updateSettings({ height : height, width : baseWidth });
        //HOT.render();
        }

      /* サイズ調整関数呼び出しインターフェイス*/
      HOT.doAdjust = adjuster;

      return HOT;
    }

    /**
    * 自動アジャスト
    * exReizeの仕様で同じセレクタに2こはだめです
    */
    HOT.setAutoAdjust = function(selector){
        // サイズ変更時アジャスト
        //HOT.addHook("beforeRender", function(byMe){ if (byMe){ return; } setTimeout(HOT.doAdjust,0);console.log("ADJUSTING......") });

        var container = getContainer(selector);
        /* 対象セレクタリサイズ時、アドジャストメント*/
        container.exResize(function(){ setTimeout(function(){ HOT.doAdjust(); },100); console.log("auto adjusting...") });
    }

  }

  /**
  * ボーダー定義API
  * 
  * 格子線を操作するインターフェイスの付与
  */
  this.add_HOTBorderAPI = function(HOT){
    var borders = []; // ボーダーリスト

    /* ボーダーの定義 */
    HOT.setBorder = function(fromRow,fromCol,toRow,toCol){
      borders = HOT.getSettings().customBorders;
      if ( ! (borders instanceof Array) ){ borders = [] }
      var range = {
        range :{
          from : { row : fromRow, col : fromCol },
          to : { row : toRow, col : toCol },
          },
        top : { width : 1, color:"black" },
        left : { width : 1, color:"black"},
        right : { width : 1, color:"black" },
        bottom : { width : 1, color:"black" },
      };

      /* ボーダーの追加 */
      borders.push(range);
      HOT.updateSettings({ customBorders : borders });
    }

    /* ボーダーの全削除 */
    HOT.unsetBorder = function(){
      $("div[class*='border']").remove();
      borders = HOT.getSettings().customBorders;
      HOT.updateSettings({customBorders : [] });
      HOT.render();
    }

   /* 正規表現でクラスを検索して削除*/
   HOT.addHook("beforeColumnResize",HOT.unsetBorder);
   HOT.addHook("afterColumnResize",function(){ HOT.updateSettings({customBorders : borders});HOT.render() });
   HOT.addHook("beforeRowResize",HOT.unsetBorder);
   HOT.addHook("afterRowResize",function(){ HOT.updateSettings({customBorders : borders});HOT.render() });
  }

  /**
  * セルマージAPIの追加
  *
  * セルマージ操作インターフェイスの追加
  */
  this.add_HOTMergeAPI = function(HOT){
    var prev_mergeCells = null;
    var merge_colList = [];

    /* マージ対象を解除 */
    HOT.unset_column_merged = function(){
      merge_colList.length = 0;
      return HOT;
    }

    /* マージ対象行を指定*/
    HOT.set_column_merged = function(col,state){
      merge_colList.push({col:col,state:state}); // 保存
      return HOT;
    }

    /* 対象rangeのマージ*/
    HOT.set_range_merged = function(fromRow,fromCol,toRow,toCol){
      var mergeCells = HOT.getSettings().mergeCells;
      if ( ! ( mergeCells instanceof Array ) ) { mergeCells = []; }

      var range = {
        row : fromRow,
        col : fromCol,
        rowspan : toRow - fromRow +1,
        colspan : toCol - fromCol +1
      };
      /* Update */
      mergeCells.push(range);
      HOT.updateSettings({ mergeCells : mergeCells });
      HOT.render();
      return HOT;
    }

    /* 選択セルを含む範囲のアンマージ*/
    HOT.unset_range_merged = function(row,col){
      var mergeCells = HOT.getSettings().mergeCells;
      if ( ! ( mergeCells instanceof Array ) ) { return; }

      /* 与えられたrow,colを含むマージオブジェクトを取り除く*/
      mergeCells = mergeCells.filter(function(item){
          // レンジを生成
          var rowRange = Array.from({length : item.rowspan}, (v, k) => k +item.row);
          var colRange = Array.from({length : item.colspan}, (v, k) => k +item.col);
          // 含まれているなら否定子で取り除く
          return !( rowRange.findIndex(function(val){ return row == val; }) > -1 && colRange.findIndex(function(val){return val == col}) > -1 )
        });

      /* Update */
      HOT.updateSettings({ mergeCells : mergeCells });
      HOT.render();
    }

    /* マージの開放*/
    HOT.release_merge = function(){
      prev_mergeCells = HOT.getSettings().mergeCells; // 変更前の情報を保存
      if (prev_mergeCells instanceof Object ){
        HOT.updateSettings({mergeCells : true});
      }
    }

    /* 定義済み指定カラムのマージを行う*/
    HOT.do_mergeColumns = function(){
      var tableData = HOT.getData();
      var mergeCells = []; // updateSettingsに渡すマージリスト{row,col,rowSpan,colSpan}

      /* マージ定義されたカラムごとにマージセルセットを生成する関数*/
      function calc_merge(col,state){
        /* 条件関数 */
        var stateFunc = state || function(){return true;};
        // 対象カラムの値のリストの抽出
        var target_colList = tableData.map(function(rowData){ return rowData[col] });

        /* マージ対象セル解析 */
        var context_merge_continued = 0; // マージ対象継続数
        target_colList.push(null); // ちょっとした最適化。forEachで最後のコンテキスト値チェックが不要になる

        /* forEachでセルリストをぶん回し、同じ値の列を探し、その終端でマージリストに放り込む */
        target_colList.forEach(function(value,index,ls){
          if ( index == 0 ) {return;} // 始めは無視

          /* 値が(NULLでなく)前と同じなら、マージ継続数をインクリメント */
          if ( value && ls[index-1] == value && stateFunc(tableData,index) ){ context_merge_continued += 1; }
          /* さもなくば、継続数を参照し、マージ対象を検出すれば、まーじリストを更新*/
          else if ( context_merge_continued ){
            mergeCells.push({
              row : index-1 -context_merge_continued , // マージ開始
              col : col,
              rowspan : context_merge_continued+1, // マージ範囲
              colspan : 1
            });

            /* マージコンテキスト継続数を初期化*/
            context_merge_continued = 0;
          }
        });
      }

      /* 定義に基づいてマージ対象の算出*/
      merge_colList.forEach(function(mergeDef){ calc_merge(mergeDef.col,mergeDef.state); });

      /* マージ定義 */
      prev_mergeCells = HOT.getSettings().mergeCells; // 変更前の情報を保存
      //mergeCells = old_mergeCells instanceof Array ? old_mergeCells.concat(mergeCells) : mergeCells; // 前のマージ情報も一応保存
      HOT.updateSettings({
        mergeCells :  mergeCells
        });
    }

    /* 一個前のセル結合情報を得る */
    HOT.get_prev_mergeCells = function(){
      return prev_mergeCells instanceof Array ? prev_mergeCells : [];
    }

    /* 自動マージ */
    HOT.set_autoMerge = function(){
        /* Change時マージ */
        HOT.addHook("afterChange",HOT.do_mergeColumns);
        HOT.addHook("beforeOnCellMouseDown",function(e,pos){
            HOT.unset_range_merged(pos.row,pos.col);
            });
        //HOT.addHook("afterOnCellMouseDown",HOT.do_mergeColumns);
    }

    /* マージユーティリティ : すぐバグるので避ける */
    HOT.prepare_merge = function(){
        // コピー対策
        HOT.addHook("beforeCopy",function(){ HOT.release_merge(); });
        HOT.addHook("afterCopy",HOT.do_mergeColumns);
    }

  }

  /**
  * HOTとDOMイベントの接続API
  */
  this.add_HOTDomConnectionAPI = function(HOT){
    /*
    * HOTへのDOMイベントの接続関数
    * Usage: hot.connect$Event("#id" ,"click", function(hot){ hot.updateSettings({ option : $(this).val() }) }; );
    */
    HOT.connect$Event = function(selector,eventName,handler){
      var jquery = $(selector);
      switch(eventName){
        case "click" :
          jquery.click( function(){ handler.call(jquery,HOT); } );
          break;
        case "change" :
          jquery.change( function(){ handler.call(jquery,HOT); } );
          break;
      }
    }

    /* 
    * HOTイベントをDOMに関連付ける
    * Usage : hot.hook2dom('afterChange',"#input",function(hot){ $(this).val( hot.getDataAtCell(1,2) ); });
    */
    HOT.hook2dom = function(hookName,selector,func){
      $Obj = $(selector);
      HOT.addHook(hookname, function(){ func.call($Obj,HOT) });
    }
  }

  /**
  * アライメント(右寄せ等)設定用API
  */
  this.add_HOTAlignmentAPI = function(HOT){
    var alignInfo = { middle: true, direction:"" };

    /* アライメント設定*/
    HOT.setAlignment = function(direction){
      /* Middleならミドルフラグをあげる*/
      if (direction == "Middle"){ alignInfo.middle = true }
      else { alignInfo.direction = direction }

      HOT.doAlignment(); // アライメントの実行
    }

    /* 非縦中央アライメント設定*/
    HOT.unsetMiddle = function(){
      alignInfo.middle = false; // フラグ下げるだけ
      HOT.doAlignment(); // アライメントの実行
    }

    /* アライメント定義を実行*/
    HOT.doAlignment = function(){
      // アライメントクラス名導出
      var className = (alignInfo.direction ? "ht" +alignInfo.direction : "") +( alignInfo.middle ? " htMiddle" : "" ) +" htCenter";
      // アップデート
      HOT.updateSettings({ className : className });
    }
  }

  /*
  * 単純なsetIntervalインターフェイス
  */
  this.add_HOTIntervalAPI = function(HOT){
    HOT.setInterval = function(func,interval){
      setInterval(func,interval,HOT); /* SetInterval */
    }
  }

  /**
  * セルプロパティ定義インターフェイス
  * クロージャをがんがん使う
  */
  this.add_HOTCellPropAPI = function(HOT){
    var propList = [] // { property : {cell_prop}, selector : row,col => true/false }のリスト

    /**
    * 関数主導の追加型インターフェイスを提供。効率は悪い
    * { セルプロパティ },セレクタ関数(row,col => true/false)をとる
    */
    HOT.addCellProp = function(prop,selector){
       propList.push({ prop : prop, selector : selector }); // 追加
    }

    /**
    * セルメタ主導のセルプロパティ定義インターフェイス
    */
    HOT.addCellProp_byCellMeta = function(metaName,prop){
      // メタ名主導のセレクタ.たぶんHOT.getMetaより早いでしょ
      var selector = function(row,col){
        if (!HOT.metaMap){ return; }
        return HOT.metaMap.get(row+","+col) == metaName;
      }
      HOT.addCellProp(prop,selector);
    }

    /* セルプロパティ定義関数 */
    var cells = function(row,col){
      var cell_prop = {};
      /* ぐるぐるしてセレクタにマッチするならアサイン */
      propList.forEach(function(elem){
        if (elem.selector(row,col)){
          cell_prop = Object.assign(cell_prop,elem.prop);
        }
      });
      return cell_prop;
    }

    /* アプライ*/
    HOT.apply_cellProp = function(){
        HOT.updateSettings({ cells : cells });
    }

    /* デフォルトでアプライしちゃいます */
    HOT.apply_cellProp();
  }

  /**
  * コンテキストメニューAPI
  * コンテキストメニューへのアクセサを提供
  */
  this.add_HOTContextMenuAPI = function(HOT){
    /* コンテキストメニューを追加させる */
    HOT.addContextMenu = function(name,callback){
        /* コンテキストメニューデータのコンストラクション */
        var item = {
            name : name, // 表示名
            callback : callback // コールバック関数
        };
        // 追加
        HOT.getSettings().contextMenu.items[name] = item;
    }
  }
}



/**
* HOT拡張修飾クラス
* 基本修飾機構のほか、通信、レンダラといった高度な抽象化された機能ベースを
* 利用する為のインターフェイスを付与する
*/
function Extended_HOTModifier(){
  HOTModifier.call(this) // 継承
  var super_init = this.init;
  var self = this;

  /*
  * 初期化関数
  * 同時にコモンAPIの初期化
  */
  this.init = function(hot){
    /* super初期化 */
    super_init(hot);
    /* コモンAPIの初期化 */
    self.add_commonAPI();

    return self;
  }

  /**
  * 全拡張APIをオープン
  */
  this.add_allAPI = function(HOT){
    HOT = self.hot || HOT;
    /* 全Extended-APIの初期化*/
    self.add_HOTRendererAPI();
    self.add_HOTAjaxAPI();
    self.add_HOTSocketAPI();
    self.add_HOTMetaMapperAPI();

    return self;
  }

  /**
  * カスタムレンダラAPI
  *
  * カスタムレンダラを初期化し、HOTオブジェクトにアクセスAPIを提供
  */
  this.add_HOTRendererAPI = function(HOT){
    HOT = self.hot || HOT;
    // カスタムレンダラの初期化
    var renderer = new HOTRenderer().init(HOT);
    // アクセサの提供
    HOT.getHOTRenderer = function(){ return renderer; }
    return self;
  }

  /**
  * Ajax送信管理API
  * Ajax送信マネージャを初期化し、アクセスAPIを付与
  */
  this.add_HOTAjaxAPI = function(HOT){
    HOT = self.hot || HOT;
    // 送信管理クラスの初期化
    new HOTAjaxManager().init(HOT);
    return self;
  }

  /**
  * Socket送受信管理API
  * Socket送信マネージャを初期化し、アクセスAPIを付与
  */
  this.add_HOTSocketAPI = function(HOT){
    HOT = self.hot || HOT;
    // ソケット管理クラスの初期化
    new HOTSocketManager().init(HOT);
    return self;
  }

  /**
  * めたまっぱAPI
  * メタマッピングマネージャを初期化し、アクセスAPIを付与
  */
  this.add_HOTMetaMapperAPI = function(HOT){
    HOT = self.hot || HOT;
    // メタマッパの初期化
    new HOTMetaMapper().init(HOT);
    return self;
  }

}


/**
* HOTのカスタムレンダラークラス
*
* 初期化時、HOTオブジェクトに機能アクセス用APIを付与する
*/
function HOTRenderer(){
  // base Renderer
  this.base_renderer = null;

  // カスタムレンダリング定義
  this.customData = new Map();
  this.readonly_color = null;

  // methods
  var self = this;

  /* ハイライト辞書のキーに使える ハッシュ可能なタプルオブジェクトが無いので、POS情報を文字列に変えるしょうもないハック */
  var pos2key = function(row,col){ return row +"," +col; }

  /* 初期化関数 */
  this.init = function(hot){
    // HOTベースレンダラの取得
    self.base_renderer = Handsontable.renderers.getRenderer('text');
    // レンダラの登録
    hot.updateSettings({
      renderer : self.render
    });

    // HOTオブジェクトにカスタムレンダリングAPIを追加
    self.set_hot_api(hot);

    self.hot = hot;
    return self;
  }

  /**
  * カスタムレンダリング関数
  */
  this.render = function(hot,td,row,col,prop,val,cellProp){
    /* HOTベースレンダリング*/
    self.base_renderer.apply(this,arguments);
    //Handsontable.renderers.BaseRenderer.apply(this, arguments);

    if ( hot !== self.hot ){return;}

    /* 組み込みreadOnly処理 */
    if ( self.readonly_color && cellProp.readOnly ){
      var className = "hot-highlight-" +self.readonly_color;
      Handsontable.dom.addClass(td,className); /* レガシーTDへのクラスの付加 */
      return;
    }

    /* 処理中のposに定義されたカスタムデータを取得*/
    var customInfo = self.customData.get(pos2key(row,col));
    if ( ! customInfo ){ return; }
    /* フォントサイズ処理 */
    if ( fontsize = customInfo["fontsize"] ){
      Handsontable.dom.addClass(td,"hot-fontsize-"+fontsize);
    }
    /* ハイライト処理 */
    if ( color = customInfo["color"] ){
      var className = "hot-highlight-" +color;
      Handsontable.dom.addClass(td,className); /* レガシーTDへのクラスの付加 */
      if ( customInfo.life ){ /* 寿命が定義されていれば..*/
        /* 寿命周りの処理 */
        setTimeout(function(){
          Handsontable.dom.removeClass(td,className); // 色を消す
          customInfo["color"] = ""; // 色づけレンダリング設定から削除
          //hot.render();
          },
          customInfo["life"]
          );
      };
    }
  }

  /**
  * カスタムレンダリングAPIをHOTオブジェクトに追加
  */
  this.set_hot_api = function(hot){
    /* HOTへのハイライト関数の追加*/
    // 行ハイライト
    hot.setRowHighlight = function(row,color,life){
      var col_len = hot.countCols(); // カラム数を見る
      /* rangeつくってぶん回し */
      Array.from({length : col_len}, (v, k) => k) .forEach(function(col){
        self.addCustomInfo(row,col,{ color : color, life : life });
        });
      return hot;
      };
    // 列はいらいと
    hot.setColHighlight = function(col,color,life){
      var row_len = hot.countRows(); // 行数を見る
      /* rangeつくってぶん回し */
      Array.from({length : row_len}, (v, k) => k) .forEach(function(row){
        self.addCustomInfo(row,col,{ color : color, life : life });
        });
      return hot;
      };
    // セルハイライト
    hot.setCellHighlight = function(row,col,color,life){
      self.addCustomInfo(row,col,{ color : color, life : life });
      return hot;
      };
    // すべてアンセット
    hot.unsetHighlight_all = function(){
      ; // 考え中
      };

    /* フォントサイズ変更関数*/
    hot.setFontsize = function(row,col,fontsize){
      self.addCustomInfo(row,col,{ fontsize : fontsize });
      return hot;
    }
  }

  /* カスタム情報定義関数 */
  this.addCustomInfo = function(row,col,data){
    // データがあればそれにアサイン
    if ( sourceData = self.customData.get( pos2key(row,col) ) ){
      Object.assign(data, sourceData );
    } else { // 無ければそのまま保存
      self.customData.set( pos2key(row,col), data );
    }
  }

  /**
  * ReadOnly非活性色化
  */
  this.set_readonly_color = function(){
    self.readonly_color = "disabled";
  }

}


/**
* HOTデータ更新同期処理インターフェイス
*
* 初期化時、HOTオブジェクトにAjax通信機能を付与する
*/
function HOTAjaxManager(){
  var self = this;
  /* 初期化関数 */
  this.init = function(hot){
    self.hot = hot;
    self.add_hot_API(hot);
  }

  /**
  * API定義
  */
  this.add_hot_API = function(HOT){
    /**
    * データ取得関数
    */
    HOT.loadData_from = function(url,data,data_processor,afterHandler,context){
      var error = function(status,text){alert("データの取得に失敗しました");console.log(status);console.log(text);}
      /* 読み込みをする */
      $.ajax({
        type: "POST",
        url: url,
        data : data || {},
        dataType: "json",
        timeout: 30000,
      })
      .done(function(data){ data_processor(data); afterHandler && afterHandler.call(context||HOT); }) // データのパースをアフターハンドらの呼び出し
      .error(error);

      console.log("sending data..."); console.log(data);
    }

    /**
    * テーブル更新時、データ自動送信機構設定API。
    * 引数に成功ハンドラ、失敗ハンドﾗ、送信データコンストラクタをとる
    * また、送信データコンストラクタは、更新情報を取るとともに、データ送信の抑制が可能なので、簡易ハックとして、高度な中間処理を行いうる。
    */
    HOT.setSyncAjaxTransmission = function(url,dataConstructor,successHandler,errorHandler){
      // 失敗時デフォルト処理
      errorHandler = errorHandler || function(e){console.log(e);throw "送信に失敗しました";}

      /* データ送信関数 */
      function sendData(changes,source){
        setTimeout(function(){
          // ロード時 OR ソースでNoTrans指定
          if ( source == "loadData" || source == "NoSyncTransmission" ){return;}

          // changesのフィルタリング
          changes = changes.filter(function(change){ return change[2] != change[3]; });
          if ( ! changes.length ){ return ; }

          /* データコンストラクション*/
          var data = dataConstructor.call(HOT,changes);
          if (!data){return;} //データが偽なら抑止
          console.log(data);

          /* データの送信 */
          $.ajax({
            url: url,
            type: "POST",
            data: data
          })
          .done(successHandler) // 成功ハンドらの呼び出し
          .fail(errorHandler); // 失敗ハンドらの呼び出し

          console.log("send data : "+data);
        },0);
      }

      // 変更時送信定義
      HOT.addHook("afterChange",sendData);
    }

    /**
    * 削除/インサート情報の同期通信機構
    */
    HOT.setSyncCreateRemovalTransmission = function(url,dataConstructor,successHandler,errorHandler){
      // 失敗時デフォルト処理
      errorHandler = errorHandler || function(e){console.log(e);throw "送信に失敗しました";}

      /* 行削除時呼び出し関数 */
      function sendData(index,amount,source){
        /* ソースでフィルタ*/
        if ( source == "auto" ){ console.log("avoid sending data"); return ; /* 自動追加にあわせてたら滅茶苦茶ですよ。*/ }

        setTimeout(function(){
          /* データのコンストラクション */
          var data = dataConstructor.call(HOT,index,amount);
          console.log(data);

          $.ajax({ /* 送信 */
            url : url,
            type: "POST",
            data: data
          })
          .done(successHandler) // 成功ハンドらの呼び出し めちゃくちゃやってます。
          .fail(errorHandler); // 失敗ハンドらの呼び出し

          console.log("send data : "+data);
        },0);
      }

      /* イベントフックに定義 */
      HOT.addHook("afterRemoveCol",sendData); // 削除時送信定義
      HOT.addHook("afterCreateCol",sendData); // 削除時送信定義
      HOT.addHook("afterRemoveRow",sendData); // 削除時送信定義
      HOT.addHook("afterCreateRow",sendData); // 削除時送信定義
    }

  }
}


/**
* ソケット通信ためのインターフェイス
*
* 初期化時、HOTオブジェクトにソケット通信機能を付与する
*/
function HOTSocketManager(){
  var self = this;
  /* 初期化関数 */
  this.init = function(hot){
    self.hot = hot;
    self.init_socketEvent();
    self.add_hot_API(hot);

    return self;
  }

  /**
  * ソケットイベントの初期化
  */
  this.init_socketEvent = function(){
    self.onopen = function(){ console.log("connection is opened"); };
    self.onerror = function(e){ alert("HOTSocket Connection Error"); };
    self.onmessage = function(msg){ console.log("get message" +msg); };
  }

  /**
  * ソケットイベント定義
  */
  this.setOnopen = function(func){
    self.onopen = func;
    return self;
  }
  this.setOnerror = function(func){
    self.onerror = func;
    return self;
  }
  this.setOnmessage = function(func){
    self.onmessage = func;
    return self;
  }

  /**
  * API定義
  */
  this.add_hot_API = function(HOT){
    /**
    * ソケットマネージャの取得
    */
    HOT.getHOTSocketManager = function(){
      return self;
    }

    /*
    * ソケットコネクションの確立
    */
    HOT.connect = function(url){
      url = "ws://" +url;
      /* コネクションの確立 */
      self.con = new WebSocket(url);
      /* イベントの設定 */
      self.con.onopen = self.onopen;
      self.con.onclose = self.onclose;
      self.con.onmessage = self.onmessage;

      /* 行儀よくページはなれる際にクローズ*/
     $(window).bind("beforeunload", function(){ self.con.close(); });
    }

    /**
    * テーブル更新時、データ自動送信機構設定API。
    * 引数に成功ハンドラ(生成関数)、失敗ハンドﾗ、送信データコンストラクタをとる
    * また、送信データコンストラクタは、更新情報を取るとともに、データ送信の抑制が可能なので、簡易ハックとして、高度な中間処理を行いうる。
    */
    HOT.setSyncSocketTransmission = function(url,dataConstructor,afterHandler){
      /* データ送信関数 */
      function sendData(changes,source){
        setTimeout(function(){
          // ロード時 OR ソースでNoTrans指定
          if ( source == "loadData" || source == "NoSyncTransmission" ){return;}

          // 編集カラムごとに送信処理
          changes.forEach(function(change){
            // 更新情報
            var row = change[0];
            var col = change[1];
            var oldVal = change[2];
            var val = change[3];

            // 更新の必要なし
            if (oldVal == val){return;}

           /* 変更情報オブジェクト*/
            var data = dataConstructor.call(HOT,change); // 引数のデータコンストラクタにより生成
            if (!data){return;} //データが偽なら抑止
            console.log(data);

            /* データの送信 */
            self.con.send(data);
            /* アフターハンドラ*/
            afterHandler.call(HOT);
            console.log("send data : "+data);
          });
        },0);
      }
      // 変更時送信定義
      HOT.addHook("afterChange",sendData);
    }

  }

}


/**
* HOTグルーピングオブジェクト
*
* 複数のHOTオブジェクトの操作を管理する
*
* ちょっと変なモデルを追加。
* 親グループはすべてのサブグループの有するHOTオブジェクトを自動で参照する
* 名前の重複は上書きされる。
*
* このモデルの導入理由は、サブグループを定義するさい、全体を定義するグループ定義と
* 定義内容が大きく重複することがあるからである。
*/
function HOTGroup(){
  // Attr 
  this.member = new Map();
  this.subGroups = new Map();
  this.parentGroup = null;

  var self = this;
  /* Methods */
  /* グループで初期化しちゃうよん*/
  this.initializeHOT = function(div_list,settings){
    // divIDでくるくる
    for ( div of div_list ){
        if ( div instanceof Array ){ // 配列のネストなら[divID,groupName]と扱う
            div = div[0];
            name = div[1];
        } else {
            name = div;
        }

        // HOT初期化
        console.log("HOTGroup initialize HOT..." +div)
        var hot = initializeHOT(div,settings);
        
        // 自身に登録
        this.add(hot,name);
    }
    return self;
  }

  /* メンバー追加 */
  this.add = function(hot,name){
    // 親グループがあれば上にもあげる
    if (self.parentGroup && name){
        self.parentGroup.add(hot,name);
    }

    // 一意な名前のデフォルト値
    name = name || new Date().getTime().toString(16)+ Math.floor(1000*Math.random()).toString(16);
    self.member.set(name,hot);
    return self;
  }

  /* メンバ取得*/
  this.get = function(name){
    return self.member.get(name);
  }

  /* サブグループ生成 */
  this.genSubGroup = function(groupName){
    var subGroup = new HOTGroup();
    self.subGroups.set(groupName,subGroup);
    subGroup.parentGroup = self;// 親定義
    return subGroup;
  }

  /* サブグループ取得 */
  this.getSubGroup = function(groupName){
    return self.subGroups.get(groupName);
  }

  /* eachイディオム */
  this.each = function(func){
    self.member.forEach(func);
  }

  /* eachでtimeout*/
  this.setTimeout = function(func,delay){
    setTimeout(function(){
      self.each(func);
    },delay||0);
  }

  /* timeout生成シンタックスシュガー */
  this.createTimeout = function(func,delay){
    return function(){
      self.setTimeout(func,delay);
    };
  }

  /*
  * HOT間のイベントバインディング
  * usage : HOTGroup.bindHook("data","main","afterChange",function(changes){
  *   this.to.setDataAtCell(0,0,change[0][3]);
  *   } });
  */
  this.bindHook = function(from,to,hookName,func){
    /* 呼び出しコンテキスト生成 */
    if (from == null){ // 全メンバについて呼び出し
        return self.member.forEach( (val,key) => {
            self.bindHook(key,to,hookName,func);
        });
    }
    var from = self.get(from);
    var to = self.get(to);
    var context = { from: from, to:to };

    /* bindHook */
    from.addHook(hookName,function(){
      func.apply(context,arguments);
    });
  }

}


/**
* メタ情報処理クラス
* メタ名と座標情報のマッピングを管理する
*
* メタ情報マッピングアーキテクチャ
* 1 : メタ定義ポインタ情報(サーバーサイドDBより参照)を消極的条件に変換 (pointerTranslator)
* 2 : 消極的条件を元に、データ主導積極的条件に変換 (applyMeta)
*
* また、メタに(として)関連付けられる「修飾」情報もまた、
* このクラスの処理範囲
*
*/
function HOTMetaMapper(){
  // Attr
  this.metaMap = new Map(); /* メタ名と消極的関数のセット */
  this.modMap = new Map(); /* メタ名と修飾情報オブジェクトのセット */
  this.pointerTranslator = null ; // ポインタトランスレイタ

  // methods
  var self = this;
  /* 初期化処理*/
  this.init = function(hot){
    self.hot = hot;
    self.init_hotAPI(hot);
    self.setPointerTranslator("default"); // デフォルトトランスレイタ
  }

  /* HOTAPI初期化 */
  this.init_hotAPI = function(hot){
    /* まっぱ取得API */
    hot.getHOTMetaMapper = function(){
      return self;
    }
    /* シンタックスシュガー提供 */
    hot.addMap = self.addMap;
    hot.addMod = self.addMod;
    hot.applyMeta = self.applyMeta;
    /* 選択中セルのめた取得シンタックス主が－*/
    hot.getSelectedMeta = function(){
      var selected = self.hot.getSelectedPos();
      return self.hot.getCellMeta(selected[0],selected[1]).meta;
    }
  }

  /*
  * マッピング定義
  * ポインタをとり、消極的条件関数に変換して、保存
  */
  this.addMap = function(metaName,pointer){
    /* 条件関数に変換 */
    var condition = self.translatePointer(pointer);
    /* マッピング */
    self.metaMap.set(metaName,condition);
  }

  /**
  * 就職情報定義
  */
  this.addMod = function(metaName,modInfo){
    /* すでにあればassign */
    if ( self.modMap.has(metaName) ){
      Object.assign(self.modMap.get(metaName),modInfo); //アサイン
    } else {
      self.modMap.set(metaName,modInfo);
    }
  }

  /**
  * ポインタ条件関数変換器定義
  */
  this.setPointerTranslator = function(func){
    if ( func == "default" ){
      func = self.defaultPointerTranslator;
    }
    self.pointerTranslator = func;
  }

  /**
  * ポインタ形式オブジェクトを、消極的条件関数に変換
  */
  this.translatePointer = function(pointer){
    return self.pointerTranslator(pointer)
  }

  /**
  * デフォルトのポインタトランスレイタ
  * ポインタデータを消極的条件関数に変換
  */
  this.defaultPointerTranslator = function(pointer){
    if ( !pointer.row ){ 
      /* rowが無ければカラムで同定 */
      return function(row,col){ return col == pointer.col; };
    } else if ( !pointer.col ){
      /* colが無ければrowで検索 */
      return function(row,col){ return row == pointer.row; };
    } else {
      /* セル条件 */
      return function(row,col){ return row == pointer.row && col == pointer.col; };
    }
  }

  /**
  * 消極的条件関数からメタを逆参照する
  */
  this.findMeta = function(row,col){
    var meta = null;
    self.metaMap.forEach(function(val,key){
      if ( val(row,col) ){ meta = key; }
    });
    return meta;
  }

  /**
  * 消極的条件関数をつかって、データ主導積極的条件に変換
  */
  this.applyMeta = function(){
    /* なんかgetCellMetaがSettings.cellsを呼んでめんどいので自分で束縛*/
    self.hot.metaMap = new Map();

    // シンプルにHOTの座標範囲でくるくるしてセルメタ定義
    var col_range = self.hot.getColRange();
    self.hot.getRowRange().forEach(function(row){
      col_range.forEach(function(col){

        /* マッチするメタの取得 */
        var meta = self.findMeta(row,col);
        if ( meta ){
          /* データ主導メタ定義 */
          self.hot.setCellMeta(row,col,"meta",meta);
        }

        /* ついでにparseModする*/
        var mod_prop = self.modMap.get(meta) || {};
        self.parseMod(row,col,mod_prop);

        // metaList束縛
        self.hot.metaMap.set(row+","+col,meta);

      });
    });
  }

  /**
  * ユーザー定義Mod情報処理
  */
  this.parseMod = function(row,col,prop){
    /* ハイライト定義 */
    if (prop.highlight){
      var color = prop.highlight;
      self.hot.setCellHighlight(row,col,color);
    }
  }

}



