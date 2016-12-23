__author__ = 'ericsage'

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

from diffusiond.diffusion import Diffuser

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

def logTime(timer, message):
    """Logs a standard message indicating an elapsed time"""
    logging.info('It took ' + str(time.time()-timer) + ' seconds to ' + message)

def CX_to_NetworkN(CX):
    """Converts CX terms into a NetworkN object"""
    try:
        timer = time.time()
        logging.info('Converting the CX structure to a NetworkN object')
        networkN = NdexGraph(CX)
        logTime(timer, 'create a networkN object')
        return networkN
    except Exception as error:
        raise Exception('Could not convert CX to a NetworkN object, error: ' + str(error))

def extract_json(request):
    """Extracts a JSON body from the request or throws an error"""
    timer = time.time()
    logging.info('Extracting json from request')
    JSON = request.get_json()
    if JSON == None:
        logging.error('Recieved None when extracting the JSON body from the request')
        raise Exception('No JSON body! Make sure the MIME type is application/json and JSON body exists')
    logTime(timer, 'decode the JSON request')
    return JSON

def parse_CX_body(request):
    """Parses the request CX document, extracting a subnetwork if one was specified"""
    CX = extract_json(request)
    subnet_id = request.args.get('subnetworkid', None, int)
    logging.info('Checking for a subnetwork Id')
    if subnet_id:
        logging.info('Found subnetwork id ' + str(subnet_id))
        CX = extract_subnetwork(CX, subnet_id)
    else:
        logging.info('No subnetwork Id found')
    return CX

def extract_subnetwork(CX, subnet_id):
    """Extracts the subnetwork with subnet_id from the CX structure"""
    try:
        timer = time.time()
        logging.info('Extracting subnetwork ' + str(subnet_id) + ' from CX')
        CX = FilterSub(CX, subnetwork_id=subnet_id).get_cx()
        logTime(timer, 'extract the subnetwork')
        return CX
    except Exception as error:
        raise Exception('Could not extract subnetwork from CX, does the subnetwork exist? Error: ' + str(error))

def diffuse(networkN, options):
    """Starts the diffuse and feeds it a network and options dictonary"""
    try:
        timer = time.time()
        logging.info('Creating new Diffuser')
        diffuser = Diffuser(networkN, options)
        logging.info('Starting diffusion')
        diffuser.start()
        logTime(timer, 'diffuse')
        return (diffuser.node_dict, diffuser.node_dict_rank)
    except Exception as error:
        raise Exception('Diffuser could not process network with options, error: ' + str(error))

def merge_heats_and_ranks(heats, ranks):
   """Merges two node dictionarys containing the node heats and node heat ranks"""
   try:
       timer = time.time()
       logging.info('Diffusion completed, now merging heats and ranks')
       merged = {key: { 'heat': heat, 'rank': ranks[key]} for (key, heat) in heats.iteritems() }
       logTime(timer, 'merge heats and ranks')
       return merged
   except Exception as error:
       raise Exception('Failed to merge heat and rank diffusion output dictionaries, error: ' + str(error))

@app.errorhandler(Exception)
def internal_error(error):
    logging.info('Caught an error! Error: ' + str(error))
    return jsonify(data={}, errors=[{'message': '500: ' + str(error)}]), 500

@app.errorhandler(400)
def bad_request_error(error):
    logging.info('Bad request, sending error message')
    return jsonify(data={}, errors=[{'message': '400: Bad Request, did you send a CX body?'}]), 400

@app.errorhandler(405)
def method_not_allowed_error(error):
    logging.info('Incorrect HTTP method used, sending error message')
    return jsonify(data={}, errors=[{'message': '405: Method not allowed, heat diffusion only accepts POST requests'}]), 405

@app.route('/', methods=['POST'])
def service():
    """Diffuses a network represented as cx against an identifier_set"""
    logging.info('Request received')
    CX = parse_CX_body(request)
    networkN = CX_to_NetworkN(CX)
    (heats, ranks) = diffuse(networkN, request.args)
    data = merge_heats_and_ranks(heats, ranks)
    logging.info('Finished, responding to the request now')
    return jsonify(data=data, errors=[])

def main():
    """Starts the diffusion service listening on port 80"""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.info('Creating the heat diffusion server')
    http_server = WSGIServer(('0.0.0.0', 80), jsonApp(app))
    logging.info('Starting the heat diffusion service on 0.0.0.0:80')
    http_server.serve_forever()
