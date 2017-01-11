#!/bin/python
"""Diffuse a set of node heats against a network.

A web service that listens on port 80 for a single top level route. Request must be a POST
with a MIME type of application/json and a valid CX body. Additional parameters included via
the url query string. Returns a JSON dictionary of nodes mapped to output heats and ranks.
"""

import sys
import logging
import time

from gevent.wsgi import WSGIServer
from flask import Flask, request, jsonify
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from ndex.networkn import NdexGraph, FilterSub

import config
import diffuser

app = Flask(__name__)

def jsonApp(app):
    """Converts all flask errors to JSON"""

    def make_json_error(error):
        response = jsonify(data={}, errors=[{'message': str(error)}])
        response.status_code = (error.code
                                if isinstance(error, HTTPException)
                                else 500)
        return response

    for code in default_exceptions.iterkeys():
        if code != 500 and code != 405 and code != 400:
            app.register_error_handler(code, make_json_error)
    return app

def get_log(message_type, message=''):
    return { 'code': message_type, 'message': config.LOG_MESSAGES[message_type] +  str(message)}

def log_info(message_type, message=''):
    if config.LOGGING:
        logging.info(get_log(message_type, message))

def get_error(error_type, error=''):
    return { 'code': error_type, 'message': config.ERROR_MESSAGES[error_type] + str(error)}

def log_error(error_type, error=''):
    if config.LOGGING:
        logging.error(get_error(error_type, error))

def raise_exception(error_type, error=''):
    log_error(error_type, error)
    raise Exception(get_error(error_type, error))

def CX_to_NetworkN(CX):
    """Converts CX terms into a NetworkN object"""
    try:
        log_info('CONVERTING_CX')
        networkN = NdexGraph(CX)
        return networkN
    except Exception as error:
        raise_exception('CX_TO_NETWORKN_CONVERSION_ERROR', error=error)

def extract_json(request):
    """Extracts a JSON body from the request or throws an error"""
    log_info('EXTRACTING_JSON')
    JSON = request.get_json('EXTRACT_JSON')
    if JSON == None:
        raise_exception('NO_JSON_BODY_ERROR')
    return JSON

def parse_CX_body(request):
    """Parses the request CX document, extracting a subnetwork if one was specified"""
    CX = extract_json(request)
    subnet_id = request.args.get('subnetworkid', None, int)
    log_info('CHECK_SUBNET_EXISTS')
    if subnet_id:
        log_info('SUBNET_ID_EXISTS', message=str(subnet_id))
        CX = extract_subnetwork(CX, subnet_id)
    else:
        log_info('SUBNET_ID_DOES_NOT_EXIST')
    return CX

def extract_subnetwork(CX, subnet_id):
    """Extracts the subnetwork with subnet_id from the CX structure"""
    try:
        log_info('EXTRACTING_SUBNETWORK')
        CX = FilterSub(CX, subnetwork_id=subnet_id).get_cx()
        return CX
    except Exception as error:
        raise_exception('EXTRACTING_SUBNETWORK_ERROR', error=error)

def diffuse(networkN, options):
    """Starts the diffuse and feeds it a network and options dictonary"""
    try:
        log_info('DIFFUSER_INITIALIZING')
        heat_diffuser = diffuser.Diffuser(networkN, options)
        log_info('DIFFUSING')
        heat_diffuser.start()
        return (heat_diffuser.node_dict, heat_diffuser.node_dict_rank)
    except Exception as error:
        raise_exception('DIFFUSER_ERROR', error=str(error))

def merge_heats_and_ranks(heats, ranks):
   """Merges two node dictionarys containing the node heats and node heat ranks"""
   try:
       log_info('DIFFUSION_COMPLETE')
       merged = {key: { 'heat': heat, 'rank': ranks[key]} for (key, heat) in heats.iteritems() }
       return merged
   except Exception as error:
       raise_exception('MERGE_OUTPUT_ERROR', error=str(error))

@app.errorhandler(Exception)
def internal_error(error):
    error_type = 'UNEXPECTED_INTERNAL_ERROR'
    log_error(error_type, error=error)
    return create_response(errors=[get_error(error_type, error)], code=500)

@app.errorhandler(400)
def bad_request_error(error):
    error_type = 'BAD_REQUEST_ERROR'
    log_error(error_type, error=error)
    return create_response(errors=[get_error(error_type, error)], code=400)

@app.errorhandler(405)
def method_not_allowed_error(error):
    error_type = 'METHOD_NOT_ALLOWED_ERROR'
    log_error(error_type, error)
    return create_response(errors=[error], code=405)

def create_response(data={}, errors=[], code=200):
    return jsonify(data=data, errors=errors), code

@app.route('/', methods=['POST'])
def service():
    """Diffuses a network represented as cx against an identifier_set"""
    log_info('REQUEST_RECEIVED')
    CX = parse_CX_body(request)
    networkN = CX_to_NetworkN(CX)
    (heats, ranks) = diffuse(networkN, request.args)
    data = merge_heats_and_ranks(heats, ranks)
    log_info('RESPONDING')
    return create_response(data=data)

def start():
    """Starts the diffusion service listening on port 80"""
    if config.LOGGING:
        logging.basicConfig(stream=sys.stdout, level=config.LOG_LEVEL, format='%(asctime)s %(message)s')
    log_info('SERVER_INITIALIZING')
    http_server = WSGIServer((config.ADDRESS, config.PORT), jsonApp(app))
    log_info('SERVER_READY')
    http_server.serve_forever()
