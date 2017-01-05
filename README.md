#Diffusiond
Provides a daemon capable of servicing heat diffusion tasks on networks provided as cx or stored in NDEx.  For details see the manuscript "Network propagation in the Cytoscape Cyberinfrastructure. Carlin DE et al. Submitted to PLoS Computational Biology."

##POST diffuse.cytoscape.io
The only route provided by this service is / the top level. Use this route to diffuse a vector of node heats against a network.


###Input
The service recieves input through the body of a POST request and optionally through the request's query string parameters. Read below for more information about the expected format of the body and the available query string paramters that you can use to tweak the heat diffusion algorithm.

####Request Body

MIME type must be `application/json`

The body must be a CX document, which will be encoded as JSON. If a heatvector is not given in the query string parameters, at least
one node needs to have a node attribute called 'diffusion_input' or whatever the query string parameter heatattribute is set to. The value
of this attribute must be a Double in the range 0 to 1 representing the initial node heat.

###Query String Parameters
Query string parameters can be used to tweak the heat diffusion alogrithm and also to send a base64 encoded list or dictionary of node heats via the heatvector parameter. Sending the heatvector parameters will override any initial heats set in the CX body. For example, you can create the correct query string value in Python like so:

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
The heat diffusion service always responds with a json object containing two keys, data and error. If the service could complete your request, data should be a dictonary of node names with heat and rank objects as values. Here is a sample call below using curl:

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
}```

If the call was not succesful, there should be an error object in the list of errors. Here is a sample bad call below using curl:

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
}```
