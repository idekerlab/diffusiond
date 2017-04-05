#Diffusiond
Provides a daemon capable of servicing heat diffusion tasks on networks provided as CX or stored in NDEx.  The service operates according to REST protocols. For details see the manuscript "Network propagation in the Cytoscape Cyberinfrastructure. Carlin DE et al. Submitted to PLoS Computational Biology."

##POST diffuse.cytoscape.io
The only route provided by this service is / the top level. Use this route to diffuse a vector of node heats against a network.


###Input
The service recieves input through the body of a POST request and optionally through the request's query string parameters. Read below for more information about the expected format of the body and the query string paramters that you can use to tweak the heat diffusion algorithm.

####Request Body

MIME type must be `application/json`

The body must be a CX document containing the network, and is encoded as JSON. 

The heatvector can be encoded as node attributes within the network (as Doubles in the range 0..1) or as a query string parameter.
If it is encoded in the network, nodes having heat values must provide the value in "diffusion_input" node attribute. An alternate
node attribute name can be specified as a query string parameter.

###Query String Parameters
Query string parameters can be used to tweak the heat diffusion alogrithm.

Instead of specifying heat values as network node attributes, they can be provided in the heatvector query string parameter, which 
is a base64 encoding of a Python list or dictionary. If the heatvector is specified, any heat values encoded in network attributes
are ignored.

If no heatvector is provided, heat values must be specified as network node attributes per the Request Body section 
above. The attribute name must be "diffusion_input", but can be overridden by the heatattribute query parameter.

For example, you can create a heatvector in a query string value in Python like so:

```python
import base64
import json

vector = {'node1': 0.2, 'node2': 0.4, 'node3': 0.6}
json_vector = json.dumps(vector)
encoded_vector = base64.b64encode(json_vector)
print 'The query string is ' + '?heatvector=' + encoded_vector
```


| Key           | Type         | Default Value       | Description                                                        |
| ------------- | :----------: | :-----------------: | :----------------------------------------------------------------- |
| subnetworkid  | Integer      | None                | A Cytoscape subnetwork to be extracted from a Collection           |
| time          | Double       | 0.1                 | Parameter t from equation 1 of the manuscript to indicate the extent of spread over the network |
| kernel        | Boolean      | False               | Should the diffuser calculate an intermediate kernel               |
| heatvector    | base64 dict  | ''                  | Node heats encoded in the query string, overrides CX encoded heats |
| heatattribute | String       | 'diffusion_input'   | The node attribute that contains the initial node heat as a Double |
| normalize     | Boolean      | False               | Should the Lappachian matrix be normalized                         |

###Output
The heat diffusion service always responds with a json object containing two keys: data and error. If the service could complete your request, data will be a dictonary of node names with heat and rank objects as values. Here is a sample call below using curl:

```bash 
curl -X POST -H "Content-Type: application/json" --data "@input.cx" diffuse.cytoscape.io
```

```json
{
  "data": {
    "64": {
      "heat": 1.0, 
      "rank": 0
    }
  }, 
  "errors": []
}
```

If the call was not successful, the error object will return a list of errors. Here is a sample bad call below using curl:

```bash 
curl -X POST -H "Content-Type: application/json" diffuse.cytoscape.io
```

```json
{
  "data": {}, 
  "errors": [
    {
      "message": "400: Bad Request, did you send a CX body?"
    }
  ]
}
```
