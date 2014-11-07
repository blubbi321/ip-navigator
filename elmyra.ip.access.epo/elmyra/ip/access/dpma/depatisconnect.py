# -*- coding: utf-8 -*-
# (c) 2014 Andreas Motl, Elmyra UG
from cornice.util import to_list
import requests
import xmlrpclib
from StringIO import StringIO
from lxml import etree as ET
from lxml.builder import E
from beaker.cache import cache_region
from elmyra.ip.util.numbers.normalize import normalize_patent

def run_acquisition(document_number, doctypes=None):
    numbers = to_list(document_number)
    doctypes = doctypes or 'xml'
    doctypes = to_list(doctypes)
    server = xmlrpclib.Server('***REMOVED***/RPC2')
    return server.runAcquisition(numbers, doctypes)

def fetch_xml(number):
    # ***REMOVED***/download/xml:docinfo/DE202014004373U1.xml?nodtd=1
    url_tpl = '***REMOVED***/download/xml:docinfo/{number}.xml?nodtd=1'
    url = url_tpl.format(number=number)
    response = requests.get(url, verify=False)
    return response

@cache_region('static')
def get_xml(number):
    """
    Fetch XML from EPD archive service
    """
    number_normalized = normalize_patent(number)
    response = fetch_xml(number_normalized)

    if response.status_code == 200:
        return response.content

    elif response.status_code == 404:

        # fetch number from remote source and try again once
        if run_acquisition(number_normalized):
            response = fetch_xml(number_normalized)
            if response.status_code == 200:
                return response.content

        raise KeyError('No XML document for "{0}" at DPMA'.format(number))
    else:
        raise ValueError('Retrieving XML document for "{0}" from DPMA failed'.format(number))


def get_claims_or_description(document_number, xpath):
    """
    Extract text and language from "claims" or "description" XML elements
    """

    xml = get_xml(document_number)
    tree = ET.parse(StringIO(xml))

    element = tree.xpath(xpath)[0]
    content = ET.tostring(element)
    content = content.strip(' \n')

    try:
        lang = tree.xpath(xpath + '/@olan')[0]
    except IndexError:
        lang = None

    response = {
        'xml': content,
        'lang': lang,
    }

    return response, element


def get_abstracts(document_number, xpath):
    """
    Extract text and language from "Ab" XML elements (abstracts)
    """

    xml = get_xml(document_number)
    tree = ET.parse(StringIO(xml))

    content = ''
    elements = tree.xpath(xpath)
    for element in elements:
        content += ET.tostring(element)
    content = content.strip(' \n')

    languages = tree.xpath(xpath + '/@lancode')
    languages = [item.upper() for item in languages]
    lang = ','.join(languages)

    response = {
        'xml': content,
        'lang': lang,
    }

    return response, elements


def depatisconnect_claims(document_number):
    """
    Return DEPATISconnect claims fulltext
    Manipulate XML to visually enumerate claims sections in HTML
    """
    response, content = get_claims_or_description(document_number, '/DocInfoRes/Result/application-body/claims')

    # visually enumerate list of claims
    for claim in content.xpath('claim'):

        # get number of claim section
        claim_number = claim.xpath('@num')[0]

        # put number before section
        claim.insert(0, E.span(claim_number + '. '))

        # put some space after section
        claim.append(E.br())
        claim.append(E.br())

    # re-serialize manipulated dom
    response['xml'] = ET.tostring(content)

    return response

def depatisconnect_description(document_number):
    """
    Return DEPATISconnect description fulltext
    """
    response, content = get_claims_or_description(document_number, '/DocInfoRes/Result/application-body/description')
    return response


def depatisconnect_abstracts(document_number, language=None):
    """
    Return DEPATISconnect abstract, optionally filtered by language
    """
    xpath = '/DocInfoRes/Result/Bibl/Ab'
    if language:
        xpath += '[@lancode="{0}"]'.format(language.lower())
    response, content = get_abstracts(document_number, xpath)
    return response


if __name__ == '__main__':

    # configure cache manager
    from beaker.cache import CacheManager
    from beaker.util import parse_cache_config_options
    cache_opts = {
        'cache.type': 'memory',
        'cache.regions': 'static',
    }
    cache = CacheManager(**parse_cache_config_options(cache_opts))

    print depatisconnect_abstracts('DE19653398A1', 'DE')
    #print depatisconnect_description('DE19653398A1')
