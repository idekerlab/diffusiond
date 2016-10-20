__author__ = 'decarlin'

class Diffuser:

    def __init__(self, networkN):
        logging.info('Diffuser: Initializing')
        #TODO: Process networkN
        self.network = networkN
        logging.info('Diffuser: Initialization complete')

    def start(self):
        """Diffuses the selected nodes against the network"""
        logging.info('Diffuser: Starting diffusion')
        #TODO: Perform diffusion
        logging.info('Diffuser: Diffusion completed')
        return self.network
