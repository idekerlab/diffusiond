__author__ = 'decarlin'

import sys
import logging
import json

from ndex.networkn import NdexGraph

from diffusiond.src.diffusion import Diffuser

def diffuse(CX, identifier_set):
    """Diffuses a network represented as cx against an identifier_set"""
    logging.info('Converting the CX json to the SIF format')
    networkN = cxToNetworkN(CX)
    logging.info('Creating new Diffuser')
    diffuser = Diffuser(networkN)
    logging.info('Starting diffusion')
    networkN = diffuser.start()
    logging.info('Diffusion completed, now returning the ranked entities as json to the caller')
    return NetworkNToCX(networkN)

def cxToNetworkN(CX):
    """Converts cx terms into a NetworkN object"""
    return NdexGraph(CX)

def networkNToCX(networkN):
    """Converts networkN into CX terms"""
    return networkN.to_cx()

def main():
  """Accepts a single input, CX as a string, and outputs CX as a string"""
  args = sys.argv
  num_args = len(args)
  logging.info('Diffusion service was called with {0} arguments'.format(num_args))
  if num_args != 1:
    error_message = 'Diffusion service expected 1 argument, recieved: {0}\n'.format(num_args)
    log.error(error_message)
    sys.stderr.write(error_message)
  else:
    log.info('Converting CX string to Python terms...')
    cx = json.loads(args[1])
    log.info('Setting up diffuser...')
    cx = diffuse(cx)
    log.info('Writing reply...')
    print(json.dumps(cx))
