"""Configuration options for the ehat diffusion service

There options control the network interface the service will bind to, whether the service logs, at what level,
and also provdes a dictionary of log and error messages for handling logging and respond with errors to the user.
"""

import logging

ADDRESS = '0.0.0.0'
PORT = 80

LOGGING = True
LOG_LEVEL = logging.INFO

LOG_MESSAGES = {
  'SERVER_INITIALIZING': 'Initializing heat diffusion server...',
  'SERVER_READY': 'Server ready, listening on address ' + ADDRESS + ' on port ' + str(PORT),
  'REQUEST_RECEIVED': 'Request was received, processing...',
  'CONVERTING_CX':   'Converting CX to NetworkN object...',
  'EXTRACTING_JSON': 'Extracting JSON from request...',
  'CHECK_SUBNET_EXISTS': 'Checking for a subnetwork Id...',
  'SUBNET_ID_EXISTS': 'Found subnetwork id',
  'SUBNET_ID_DOES_NOT_EXIST': 'No subnetwork Id found',
  'EXTRACTING_SUBNETWORK': 'Extracting subnetwork from CX...',
  'DIFFUSER_INITIALIZING': 'Extracing parameters and Initilaizng new diffuser...',
  'DIFFUSING': 'Diffuser now propogating heat...',
  'DIFFUSION_COMPLETE': 'Diffusion completed, now merging heat and ranks into output dictionary...',
  'RESPONDING': 'Finished, now responding to the request with the output dicitonary response body...'

}

ERROR_MESSAGES = {
  'CX_TO_NETWORKN_CONVERSION_ERROR': 'Could not convert CX to a NetworkN object, error: ',
  'NO_JSON_BODY_ERROR': 'No JSON body! Make sure the MIME type is application/json and JSON body exists',
  'EXTRACTING_SUBNETWORK_ERROR': 'Could not extract subnetwork from CX, does the subnetwork exist? Error: ',
  'DIFFUSER_ERROR': 'Diffuser could not process network with given options, error from diffuser: ',
  'MERGE_OUTPUT_ERROR': 'Failed to merge heat and rank dictionaries into output dictionary, error: ',
  'UNEXPECTED_INTERNAL_ERROR': 'An unexpected error has occured in the heat diffusion service, error: ',
  'BAD_REQUEST_ERROR': 'Bad request, 400 triggered, CX body may be missing or incorrect, error from interal server: ',
  'METHOD_NOT_ALLOWED_ERROR': 'Incorrect HTTP method used, must be POST, error from internal server: '
}
