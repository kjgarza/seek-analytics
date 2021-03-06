################################################## 
# termine_services.py 
# generated by ZSI.generate.wsdl2python
##################################################


from termine_services_types import *
import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
import ZSI

# Locator
class termineLocator:
    termine_porttype_address = "http://www.nactem.ac.uk/termine"
    def gettermine_porttypeAddress(self):
        return termineLocator.termine_porttype_address
    def gettermine_porttype(self, url=None, **kw):
        return termineSOAP(url or termineLocator.termine_porttype_address, **kw)

# Methods
class termineSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: analyze
    def analyze(self, request):
        if isinstance(request, analyze_request) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=analyze_response.typecode.ofwhat, pyclass=analyze_response.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

class analyze_request:
    def __init__(self):
        self._src = None
        self._input_format = None
        self._output_format = None
        self._stoplist = None
        self._filter = None
        return
analyze_request.typecode = Struct(pname=("urn:termine","analyze"), ofwhat=[ZSI.TC.String(pname="src", aname="_src", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="input_format", aname="_input_format", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="output_format", aname="_output_format", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="stoplist", aname="_stoplist", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="filter", aname="_filter", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=analyze_request, encoded="urn:termine")

class analyze_response:
    def __init__(self):
        self._result = None
        return
analyze_response.typecode = Struct(pname=("urn:termine","analyzeResponse"), ofwhat=[ZSI.TC.String(pname="result", aname="_result", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=analyze_response, encoded="urn:termine")
