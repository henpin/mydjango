# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template, request, Response, jsonify, send_file, make_response
from flask_tinydb import PDFFormDB

import json

import pdf_utils

app = Flask(__name__)
app.debug = True

pdfDB = PDFFormDB()
PDFApp = pdf_utils.App()

@app.route("/pdf_form")
def pdf_form():
    """ PDFフォーマット基底ページ """
    return render_template("pdf_form.html")

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
    # json抜く
    json_data = request.form["data"]
    # PDF化する
    out_file = PDFApp.production(json_data)

    return send_file(out_file, mimetype='application/pdf')

@app.route("/pdf_form/form/", methods=["POST"])
def generate_form():
    """ フォーム作る """
    # json抜く
    json_data = request.form["data"]
    # レンダリング
    print json_data
    return render_template("pdf_form.html", json_data=json_data)


if __name__ == "__main__":
    app.run()
