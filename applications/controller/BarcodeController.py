from flask_login import current_user, login_user, login_required, logout_user
from ..dao import LoginDao as loginDao
from .. import login_manager
from io import StringIO
# from xhtml2pdf import pisa
# import pytz
from time import sleep
from threading import Thread
from functools import wraps
import datetime
# import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask import current_app as app
from flask import request, render_template, make_response, jsonify, redirect, Blueprint, url_for, session
from applications.dao import BarcodeDao as barcodeDao
from applications.lib import dataTableError


@app.route('/barcode/', methods=['GET'])
@login_required
def barcode():
    return render_template("barcode.html")

@app.route('/barcode/getDataBySkuBarcode', methods=['GET'])
@login_required
def getProductBySkuBarcode():
    data = request.args.get('input')
    db_res = barcodeDao.getDataBySkuBarcode(data.upper())
    if db_res.is_error:
        return jsonify({"status": db_res.status, "message": str(db_res.pgerror)})
    return jsonify({"status": db_res.status, "message": "Berhasil Get Data", "data":db_res.result})


@app.route('/barcode/printBarcode', methods=['POST'])
@login_required
def printBarcode():
    data = request.get_json()
    return jsonify({"status": True, "message": "Berhasil Get Data", "data":render_template('barcode-print.html',data=data)})