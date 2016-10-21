__author__ = 'decarlin'

import sys
import logging
import json

from ndex.networkn import NdexGraph

from diffusiond.src.diffusion import Diffuser

def diffuse(CX):
    """Diffuses a network represented as cx against an identifier_set"""
    logging.info('Converting the CX json to the SIF format')
    networkN = CXToNetworkN(CX)
    logging.info('Creating new Diffuser')
    diffuser = Diffuser(networkN)
    logging.info('Starting diffusion')
    networkN = diffuser.start()
    logging.info('Diffusion completed, now returning the ranked entities as json to the caller')
    return networkNToCX(networkN)

def CXToNetworkN(CX):
    """Converts cx terms into a NetworkN object"""
    return NdexGraph(CX)

def networkNToCX(networkN):
    """Converts networkN into CX terms"""
    return networkN.to_cx()

def main():
  """Accepts a single input, CX as a string, and outputs CX as a string"""
  logging.basicConfig(level=logging.INFO)
  args = sys.argv
  num_args = len(args)-1
  logging.info('Diffusion service was called with {0} arguments'.format(num_args))
  if num_args != 1:
    error_message = 'Diffusion service expected 1 argument, recieved: {0}\n'.format(num_args)
    logging.error(error_message)
  else:
    logging.info('Converting CX string to Python terms...')
    print args[1]
    cx = json.loads(args[1])
    logging.info('Setting up diffuser...')
    print cx
    cx = diffuse(cx)
    logging.info('Writing reply...')
    print(json.dumps(cx))
