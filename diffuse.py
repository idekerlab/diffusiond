__author__ = 'decarlin'

"""Diffuses a set of initial node heats against a network.

This module will serve a web application on port 5000 that will accept any
valid CX network. It will extract a diffuse_input column from the nodeAttributes
of this network, and use this column to diffuse the specificed nodes with intial heats
against the network. It will then return a new column of nodes and their heats after diffusion
has taken place.
"""

import sys
import logging
import json

from flask import request, Response, Flask
from ndex.networkn import NdexGraph, FilterSub

from diffusiond.src.diffusion import Diffuser

app = Flask(__name__)

def CX_to_NetworkN(CX):
    """Converts cx terms into a NetworkN object"""
    return NdexGraph(CX)

def networkN_to_CX(networkN):
    """Converts networkN into CX terms"""
    return networkN.to_cx()

@app.route('/', methods=['POST'])
@app.route('/<int:subnetwork_id>', methods=['POST'])
def diffuse(subnetwork_id=None):
    """Diffuses a network represented as cx against an identifier_set"""
    CX = request.get_json()
    if subnetwork_id != None:
      logging.info('Extracting subnetwork ' + str(subnetwork_id) + ' from CX')
      CX = FilterSub(CX, subnetwork_id=subnetwork_id).get_cx()
    logging.info('Converting the CX json to the SIF format')
    networkN = CX_to_NetworkN(CX)
    logging.info('Creating new Diffuser')
    diffuser = Diffuser(networkN)
    logging.info('Starting diffusion')
    diffuser.start()
    logging.info('Diffusion completed, now returning the ranked entities as json to the caller')
    return Response(json.dumps(diffuser.node_dict), status=200, mimetype='application/json')

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(host='0.0.0.0')
