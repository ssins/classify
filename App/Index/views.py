from App.Index import index
from flask import Flask, request, redirect,url_for
from werkzeug import SharedDataMiddleware
@index.route('/')
def root():
    return redirect(url_for('ocr.upload_pic'))