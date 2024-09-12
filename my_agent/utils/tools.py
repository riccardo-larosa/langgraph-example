from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import requests, yaml, re
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec, ReducedOpenAPISpec

@tool
def exec_get_request(baseurl: str, endpoint: str, headers: dict = None, params: dict = None):
    """
    Executes a GET request to the specified endpoint.
    """
    response = requests.get(baseurl + endpoint, headers=headers, params=params)
    response.raise_for_status()
    #json = { "data": [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jenny Lee"}] }
    return response.json()
    
@tool
def exec_post_request(baseurl: str, endpoint: str, headers: dict = None, data: dict = None):
    """
    Executes a POST request to the specified endpoint.
    """
    response = requests.post(baseurl + endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

@tool
def exec_put_request(baseurl: str, endpoint: str, headers: dict = None, data: dict = None):
    """
    Executes a PUT request to the specified endpoint.
    """
    response = requests.put(baseurl + endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

@tool
def get_API_names_description():
    """
    Returns a list of API names and descriptions.
    """
    #url = "https://raw.githubusercontent.com/elasticpath/elasticpath-dev/main/openapispecs/catalog/catalog_view.yaml"
    url = "https://raw.githubusercontent.com/elasticpath/elasticpath-dev/main/openapispecs/pim/pim.yaml"
    response = requests.get(url)
    if response.status_code == 200:
        raw_openapi_spec = yaml.safe_load(response.text)
    else:
        raise ValueError(f"Failed to fetch OpenAPI spec: {response.text}")

    #with open("./openapispecs/catalog/catalog_view.yaml") as f:
    #    raw_openapi_spec = yaml.load(f, Loader=yaml.Loader)
    openapi_spec = reduce_openapi_spec(raw_openapi_spec, dereference=False)
    endpoint_descriptions = [
        f"{name} {description[:1000]}" if description is not None else "aaa" for name, description, _ in openapi_spec.endpoints
    ]
    endpoints =  "\n ".join(endpoint_descriptions)
    
    return endpoint_descriptions

@tool
def get_API_spec_for_endpoint(endpoint: str):
    """
    Returns the OpenAPI spec for the specified endpoint.
    """
    #url = "https://raw.githubusercontent.com/elasticpath/elasticpath-dev/main/openapispecs/catalog/catalog_view.yaml"
    url = "https://raw.githubusercontent.com/elasticpath/elasticpath-dev/main/openapispecs/pim/pim.yaml"
    response = requests.get(url)
    if response.status_code == 200:
        raw_openapi_spec = yaml.safe_load(response.text)

    openapi_spec = reduce_openapi_spec(raw_openapi_spec, dereference=False)
    pattern = r"\b(GET|POST|PATCH|DELETE|PUT)\s+(/\S+)*"
    matches = re.findall(pattern, endpoint)
    endpoint_names = [
        "{method} {route}".format(method=method, route=route.split("?")[0])
        for method, route in matches
    ]
    docs_str = ""
    for endpoint_name in endpoint_names:
        found_match = False
        for name, _, docs in openapi_spec.endpoints:
            regex_name = re.compile(re.sub(r"\{.*?\}", ".*", name))
            if regex_name.match(endpoint_name):
                found_match = True
                docs_str += f"== Docs for {endpoint_name} == \n{yaml.dump(docs)}\n"
        if not found_match:
            raise ValueError(f"{endpoint_name} endpoint does not exist.")

tools = [TavilySearchResults(max_results=1), 
         exec_get_request, 
         exec_post_request, 
         exec_put_request,
        get_API_names_description]