
import cx_pb2_grpc
import cx_pb2
import grpc
import time
from concurrent import futures
import networkx as nx
from diffuser import Diffuser

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class CyServiceServicer(cx_pb2_grpc.CyServiceServicer):

    def StreamElements(self, request_iterator, context):
        graph = nx.Graph()
        errors = []
        parameters = {}
        for element in request_iterator:
            print element
            if element.WhichOneof("value") == "error":
                error = element.error
                errors.append(error)
                yield element
            elif element.WhichOneof("value") == "node":
                node = element.node
                attrs = {'name': node.name}
                graph.add_node(node.id, attr_dict=attrs)
            elif element.WhichOneof("value") == "edge":
                edge = element.edge
                attrs = {"interaction": edge.interaction}
                graph.add_edge(edge.sourceId, edge.targetId)
            elif element.WhichOneof("value") == "nodeAttribute":
                nodeAttr = element.nodeAttribute
                attrs = {}
                if nodeAttr.name == 'diffusion_input':
                    attrs = {'diffusion_input': float(nodeAttr.value)}
                else:
                    attrs = {nodeAttr.name: nodeAttr.value}
                graph.add_node(nodeAttr.nodeId, attr_dict=attrs)
            elif element.WhichOneof("value") == "parameter":
                parameter = element.parameter
                parameters[parameter.name] = parameter.value
        print "Checking for errors"
        if len(errors) == 0:
            diffuser = Diffuser(graph, parameters)
            diffuser.start()
            for nodeid in diffuser.network.nodes_iter():
                element = cx_pb2.Element()
                attr = element.nodeAttribute
                attr.nodeId = nodeid
                attr.name = 'diffused_output'
                attr.value = str(diffuser.network.node[nodeid]['diffused_output'])
                yield element
        else:
            for blank in []:
                yield blank

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
    print "Listening on 0.0.0.0:8080..."
    serve()
