from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import requests
from my_agent.utils.utils import find_match_for_endpoint, get_OpenAPI_spec_for_endpoint

#TODO: we should probably have a class for these
def get_baseurl():
    return "https://useast.api.elasticpath.com"

def create_headers(token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return headers

@tool
def exec_get_request( endpoint: str, token: str, params: dict = None, baseurl=get_baseurl()):
    """
    Executes a GET request to the specified endpoint.
    """
    response = requests.get(baseurl + endpoint, headers=create_headers(token), params=params)
    print(requests)
    response.raise_for_status()
    
    return response.json()
    
@tool
def exec_post_request( endpoint: str, token: str, body: dict = None, baseurl=get_baseurl()):
    """
    Executes a POST request to the specified endpoint.
    """
    response = requests.post(baseurl + endpoint, headers=create_headers(token), json=body)
    response.raise_for_status()
    return response.json()

@tool
def exec_put_request( endpoint: str, token: str, body: dict = None, baseurl=get_baseurl()):
    """
    Executes a PUT request to the specified endpoint.
    """
    response = requests.put(baseurl + endpoint, headers=create_headers(token), json=body)
    response.raise_for_status()
    return response.json()


@tool
def get_API_spec(text):
    """
    Given a text string in the form of an action, returns the current api spec that will be used to execute the action.
    For instance if the text is "list all the nodes", the API spec for listing all the nodes will be returned.
    The API spec will look something like this:
    == Docs for GET /pcm/hierarchies/{hierarchyID}/nodes == 
        description: A fully paginated view of all nodes in a hierarchy regardless of depth.
        parameters:
        - description: A unique identifier for the hierarchy.
            in: path
            name: hierarchyID
            required: true
            schema:
        responses:
            content:
                application/json:

    """
    #find the appropriate API endpoint 
    api_endpoint = find_match_for_endpoint(text)
    #get the full API spec for this endpoint
    api_spec = get_OpenAPI_spec_for_endpoint(api_endpoint)
    
    return api_spec


tools = [
         exec_get_request, 
         exec_post_request, 
         exec_put_request,
         get_API_spec]

#TavilySearchResults(max_results=1), 