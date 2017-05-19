
import sys
import time
import logging
from concurrent import futures

import grpc
import networkx as nx

import cx_pb2
import cx_pb2_grpc
from diffuser import Diffuser

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class CyServiceServicer(cx_pb2_grpc.CyServiceServicer):

    def StreamElements(self, element_iterator, context):
        try:
            diffusion_parameters = {
              'time': "0.1",
              'normalize_laplacian': 'False',
              'input_attribute_name': 'diffusion_input',
              'output_attribute_name': 'diffusion_output',
              'threshold': '0.0'
            }
            network, modified_parameters, errors = self.read_element_stream(element_iterator, diffusion_parameters)
            diffusion_parameters = modified_parameters
            if len(errors) == 0:
                diffuser = Diffuser(network, diffusion_parameters)
                sorted_heats = diffuser.start()
                rank = 1
                for (node_id, heat) in sorted_heats:
                    if heat > float(diffusion_parameters['threshold']):
                        yield self.create_output_attribute(node_id, str(heat), diffusion_parameters['output_attribute_name'], '_heat')
                        yield self.create_output_attribute(node_id, str(rank), diffusion_parameters['output_attribute_name'], '_rank')
                        rank += 1
            else:
                for caught_error in errors:
                    error = self.create_internal_crash_error(caught_error.message, 500)
                    log_error(error)
                    yield error
        except Exception as e:
            message = "Unexpected error: " + str(e)
            error = self.create_internal_crash_error(message, 500)
            log_error(error)
            yield error

    def create_output_attribute(self, node_id, value, attribute_name, suffix):
        element = cx_pb2.Element()
        attr = element.nodeAttribute
        attr.nodeId = node_id
        attr.name = attribute_name + suffix
        attr.value = value
        return element

    def create_internal_crash_error(self, message, status):
        element = cx_pb2.Element()
        error = element.error
        error.status = status
        error.code = 'cy://heat-diffusion/' + str(status)
        error.message = message
        error.link = 'http://logs.cytoscape.io/heat-diffusion'
        return element

    def read_element_stream(self, element_iter, parameters):
        errors = []
        network = nx.Graph()
        for element in element_iter:
            ele_type = element.WhichOneof('value')
            if ele_type == 'error':
                errors.append(element.error)
            elif ele_type == 'parameter':
                param = element.parameter
                parameters[param.name] = param.value
            elif ele_type == 'node':
                node = element.node
                network.add_node(node.id, name=node.name)
            elif ele_type == 'edge':
                edge = element.edge
                network.add_edge(edge.sourceId, edge.targetId, interaction=edge.interaction)
            elif ele_type == 'nodeAttribute':
                nodeAttr = element.nodeAttribute
                if (nodeAttr.name == 'name'):
                    network.add_node(nodeAttr.nodeId, attr_dict={nodeAttr.name: nodeAttr.value})
                elif (nodeAttr.name == parameters['input_attribute_name']):
                    network.add_node(nodeAttr.nodeId, attr_dict={nodeAttr.name: float(nodeAttr.value)})
        return network, parameters, errors


def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cx_pb2_grpc.add_CyServiceServicer_to_server(
            CyServiceServicer(), server)
    server.add_insecure_port('0.0.0.0:8080')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(message)s')
    log_info("Listening for requests on '0.0.0.0:8080'")
    serve()
