# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template, request, Response, jsonify, send_file, make_response
from flask_tinydb import PDFFormDB

import json
import uuid
import os

import pdf_utils

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR,"static","media") # /static/media

pdfDB = PDFFormDB()
PDFApp = pdf_utils.App()

# general
def is_allowedFile(filename):
    """ docファイルか否か """
    return ( '.doc' in filename )

def gen_pdf_fileName(_uuid):
    """ UUIDからPDFファイル名を作る """
    return os.path.join(MEDIA_DIR,_uuid+".pdf")

def gen_png_fileName(_uuid,initial=False,root=True):
    """ ピングファイルを生み出す """
    if initial:
        endphrase = "_%d.png"
    else :
        endphrase = "_0.png"
        
    if root :
        return os.path.join(MEDIA_DIR,_uuid+endphrase)
    else :
        return _uuid +endphrase


# Router
@app.route("/")
def home():
    """ ワードファイルアップロード基底ペー ジ"""
    # 全フォームデータ抜く
    form_data = pdfDB.all("data")

    return render_template("home.html", form_data=form_data)

@app.route("/file_upload/upload/", methods=["POST"])
def upload_file():
    """ ファイルアップロード """
    # ファイル抜く
    _file = request.files['word_file']

    # ファイル名つくる
    if _file and is_allowedFile(_file.filename):
        # 一意名生成
        _uuid = str(uuid.uuid4())
        filename =  _uuid+".docx"
        filepath = os.path.join(MEDIA_DIR,filename)
        # 保存
        _file.save(filepath)

    else:
        return "<p>許可されていない拡張子です</p>"

    # PDFコンバータ
    pdf = pdf_utils.PDFConverter()

    # word2pdf
    out_dir = MEDIA_DIR
    pdf.word2pdf(filepath,out_dir) # 変換

    # pdf2image 
    pdf_fileName = gen_pdf_fileName(_uuid)
    png_fileName = gen_png_fileName(_uuid, initial=True)
    pdf.pdf2png(pdf_fileName,png_fileName) # さらに変換

    # コンテキスト定義
    ns = {
        "uuid" : _uuid, # 基本UUID
        "png_file" : "/static/media/" +gen_png_fileName(_uuid,root=False), # ファイル名
    }

    # フォーム作成画面レンダリング
    return render_template("pdf_form.html", ns=ns, title=u"電子帳票デザイナ")


@app.route("/pdf_form/format/save")
def save_format():
    """ フォーマットJSON保存 """
    # DBに保存
    jsonData = request.form["data"]
    data = json.loads(jsonData)
    pdfDB.insert_format(data)

    # 返す
    response = Response()
    response.status_code = 200
    return response

@app.route("/pdf_form/output/", methods=["POST"])
def output_pdf():
    """ PDFにして返す """
    # データ抜く
    json_data = request.form["data"] # JSON
    _uuid = request.form["uuid"] # uuid抜く
    data_list = json.loads(json_data) # 読む

    # テンプレPDF名参照
    pdf_fileName = gen_pdf_fileName(_uuid)
    out_fileName = gen_pdf_fileName(_uuid +"_out") # 接尾辞つけときゃOK

    # PDF化する
    with pdf_utils.PDFGenerator().init_pdf() as pdf :
        pdf.load_template(pdf_fileName) # テンプレ読む
        pdf.set_outfile(out_fileName) # 出力先読む
        for val in data_list :
            # データ抽出
            x,y = pdf.pos2lefttop(
                val["x"]/2, val["y"]/2 +val["height"]/2 # 半分
            )
            text = val["text"]
             # 書き込み
            pdf.draw_string(x,y,text)

    # PDF返す
    return send_file(out_fileName, mimetype='application/pdf')

@app.route("/pdf_form/form/create/", methods=["POST"])
def generate_form():
    """ フォーム作る """
    # データ抜く
    json_data = request.form["data"] # json抜く
    _uuid = request.form["uuid"] # uuid抜く

    # コンテキスト定義
    png_file = "/static/media/" +gen_png_fileName(_uuid,root=False)
    ns = {
        "uuid" : _uuid, # 基本UUID
        "png_file" : png_file, # ファイル名
    }

    # 保存
    pdfDB.insert_data(
        _uuid = _uuid,
        json = json_data,
        png_file = png_file
        )

    # フォーム作成画面レンダリング
    return render_template("pdf_form.html", ns=ns, json_data=json_data)

@app.route("/pdf_form/form/<string:_uuid>", methods=["GET"])
def load_form(_uuid):
    """ フォーム読み込む """
    result = pdfDB.search_data(_uuid) # リザルト抜く
    if result :
        # 値抜く
        json_data = result["json"]

        # コンテキスト構築
        ns = {
            "uuid" : _uuid, # 基本UUID
            "png_file" : "/static/media/" +gen_png_fileName(_uuid,root=False), # ファイル名
        }
        
        # フォーム作成画面レンダリング
        return render_template("pdf_form.html", ns=ns, json_data=json_data, title=u"電子フォーム入力")

    else :
        return "<p>Not Found</p>"



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

