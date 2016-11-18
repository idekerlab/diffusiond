__author__ = 'decarlin'

import sys
import logging
import json

from flask import request, Response, Flask
from ndex.networkn import NdexGraph

from diffusiond.src.diffusion import Diffuser

app = Flask(__name__)

def CX_to_NetworkN(CX):
    """Converts cx terms into a NetworkN object"""
    return NdexGraph(CX)

def networkN_to_CX(networkN):
    """Converts networkN into CX terms"""
    return networkN.to_cx()

@app.route('/', methods=['POST'])
def diffuse():
    """Diffuses a network represented as cx against an identifier_set"""
    CX = request.get_json()
    if CX == None:
        return 415
    logging.info('Converting the CX json to the SIF format')
    networkN = CX_to_NetworkN(CX)
    print networkN
    logging.info('Creating new Diffuser')
    diffuser = Diffuser(networkN)
    logging.info('Starting diffusion')
    networkN = diffuser.start()
    logging.info('Diffusion completed, now returning the ranked entities as json to the caller')
    return Response(json.dumps(networkN_to_CX(networkN)), status=200, mimetype='application/json')

def main():
    app.run(host='0.0.0.0')
