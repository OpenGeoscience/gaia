from girder.api.rest import Resource, setRawResponse
from girder.api import access
from girder.api.describe import Description
from girder.utility import config
import cherrypy
import json
from gaia.parser import GaiaRequestParser
import gaia.formats

class GeoProcess(Resource):
    """Make various gaia requests on Girder data."""

    def __init__(self):
        self.resourceName = 'geoprocess'
        self.config = config.getConfig()
        self.route('POST', (':geoprocess',), self.processTask)

    @access.public
    def processTask(self, geoprocess, params):
        """
        Based on the process name in the URL and JSON in the request body,
        create & send a WPS request and pass on the response.
        """

        json_body = self.getBodyJson()

        process = GaiaRequestParser(
            geoprocess, data=json_body).process

        # assume output is GeoJSON or GeoTIFF
        process.compute()
        result = json.loads(process.output.read(format=gaia.formats.JSON))
        if not isinstance(result, dict):
            setRawResponse(True)
            cherrypy.response.headers['Content-Type'] = 'image/tiff'
        return result

    processTask.description = (
        Description('Make a gaia request and return the response')
        .param('geoprocess', 'The process to run', paramType='path')
        .param('body', 'A JSON object containing the process parameters',
               paramType='body')
        .errorResponse('An error occurred making the request', 500))


def load(info):
    info['apiRoot'].geoprocess = GeoProcess()
