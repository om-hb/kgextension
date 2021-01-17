from kgextension import __agent__
from SPARQLWrapper import __version__
from kgextension.sparql_helper import regex_string_generator, RemoteEndpoint, LocalEndpoint, endpoint_wrapper
from kgextension.endpoints import DBpedia, WikiData, EUOpenData
import pytest
import pandas as pd
import io
import sys
import pyparsing
import xml

class TestRemoteEndpointQuerying:

    def test1_wikidata(self):

        WikiData.agent = __agent__+" (https://github.com/om-hb/kgextension; kgproject20@gmail.com) sparqlwrapper/"+__version__

        query = "SELECT ?cc WHERE {wd:Q937 wdt:P27/wdt:P1549 ?cc . FILTER (lang(?cc) = 'en')}"

        expected_result_df = pd.DataFrame({'cc': ["American", "Swiss"]})

        result = WikiData.query(query)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test2_wikidata_csv_unsupported(self):

        WikiData.agent = __agent__+" (https://github.com/om-hb/kgextension; kgproject20@gmail.com) sparqlwrapper/"+__version__
        
        query = "SELECT ?cc WHERE {wd:Q937 wdt:P27/wdt:P1549 ?cc . FILTER (lang(?cc) = 'en')}"

        expected_result_df = pd.DataFrame({'cc': ["American", "Swiss"]})

        result = WikiData.query(query, request_return_format="CSV", verbose=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test3_dbpedia(self):
        
        query = "SELECT <http://dbpedia.org/resource/University_of_Mannheim> ?chancellor ?established ?name WHERE {<http://dbpedia.org/resource/University_of_Mannheim> dbo:chancellor ?chancellor . <http://dbpedia.org/resource/University_of_Mannheim> dbp:established ?established . <http://dbpedia.org/resource/University_of_Mannheim> foaf:name ?name.}"

        expected_result_df = pd.DataFrame({
            "callret-0": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim"],
            "chancellor": ["http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm"],
            "established": ["1763", "1907", "1967", "1763", "1907", "1967"],
            "name": ["University of Mannheim", "University of Mannheim", "University of Mannheim", "Universität Mannheim", "Universität Mannheim", "Universität Mannheim"]
            })

        result = DBpedia.query(query)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test4_dbpedia_json(self):
        
        query = "SELECT <http://dbpedia.org/resource/University_of_Mannheim> ?chancellor ?established ?name WHERE {<http://dbpedia.org/resource/University_of_Mannheim> dbo:chancellor ?chancellor . <http://dbpedia.org/resource/University_of_Mannheim> dbp:established ?established . <http://dbpedia.org/resource/University_of_Mannheim> foaf:name ?name.}"

        expected_result_df = pd.DataFrame({
            "callret-0": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim"],
            "chancellor": ["http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm"],
            "established": ["1763", "1907", "1967", "1763", "1907", "1967"],
            "name": ["University of Mannheim", "University of Mannheim", "University of Mannheim", "Universität Mannheim", "Universität Mannheim", "Universität Mannheim"]
            })

        result = DBpedia.query(query, request_return_format="JSON")

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test5_dbpedia_csv(self):
        
        query = "SELECT <http://dbpedia.org/resource/University_of_Mannheim> ?chancellor ?established ?name WHERE {<http://dbpedia.org/resource/University_of_Mannheim> dbo:chancellor ?chancellor . <http://dbpedia.org/resource/University_of_Mannheim> dbp:established ?established . <http://dbpedia.org/resource/University_of_Mannheim> foaf:name ?name.}"

        expected_result_df = pd.DataFrame({
            "callret-0": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Mannheim"],
            "chancellor": ["http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm", "http://dbpedia.org/resource/Susann-Annette_Storm"],
            "established": ["1763", "1907", "1967", "1763", "1907", "1967"],
            "name": ["University of Mannheim", "University of Mannheim", "University of Mannheim", "Universität Mannheim", "Universität Mannheim", "Universität Mannheim"]
            })

        result = DBpedia.query(query, request_return_format="CSV")

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test6_eurostat(self):
        
        query = "PREFIX dcat: <http://www.w3.org/ns/dcat#> PREFIX odp: <http://data.europa.eu/euodp/ontologies/ec-odp#> PREFIX dc: <http://purl.org/dc/terms/> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT  ?DatasetTitle  ?DatasetPublisher WHERE { graph ?g  {?DatasetURI a <http://www.w3.org/ns/dcat#Dataset>; dc:publisher ?DatasetPublisher; dc:title ?DatasetTitle ; dc:modified ?DateModified FILTER(xsd:dateTime(?DateModified) > \"2013-02-28\"^^xsd:dateTime) } }  LIMIT 5"

        expected_result_df = pd.DataFrame({
            'DatasetTitle': ["Gender employment gap by NUTS 2 regions", "Geschlechtsspezifische Unterschiede bei der Beschäftigung nach NUTS-2-Regionen", "Écart d'emploi entre les hommes et les femmes par région NUTS 2","Gender employment gap by degree of urbanisation","Écart d'emploi entre les hommes et les femmes par degré d'urbanisation"],
            "DatasetPublisher": ["http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT"]
            })

        result = EUOpenData.query(query)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test7_eurostat_xml(self):
        
        query = "PREFIX dcat: <http://www.w3.org/ns/dcat#> PREFIX odp: <http://data.europa.eu/euodp/ontologies/ec-odp#> PREFIX dc: <http://purl.org/dc/terms/> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT  ?DatasetTitle  ?DatasetPublisher WHERE { graph ?g  {?DatasetURI a <http://www.w3.org/ns/dcat#Dataset>; dc:publisher ?DatasetPublisher; dc:title ?DatasetTitle ; dc:modified ?DateModified FILTER(xsd:dateTime(?DateModified) > \"2013-02-28\"^^xsd:dateTime) } }  LIMIT 5"

        expected_result_df = pd.DataFrame({
            'DatasetTitle': ["Gender employment gap by NUTS 2 regions", "Geschlechtsspezifische Unterschiede bei der Beschäftigung nach NUTS-2-Regionen", "Écart d'emploi entre les hommes et les femmes par région NUTS 2","Gender employment gap by degree of urbanisation","Écart d'emploi entre les hommes et les femmes par degré d'urbanisation"],
            "DatasetPublisher": ["http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT","http://publications.europa.eu/resource/authority/corporate-body/ESTAT"]
            })

        result = EUOpenData.query(query, request_return_format="XML")

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test8_nobleprize(self):
        
        query = "PREFIX nobel: <http://data.nobelprize.org/terms/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?label WHERE { ?laur rdf:type nobel:Laureate . ?laur rdfs:label ?label . ?laur foaf:gender \"female\" . ?laur nobel:laureateAward ?award . ?award nobel:category <http://data.nobelprize.org/resource/category/Physics> . }"

        NoblePrize = RemoteEndpoint("http://data.nobelprize.org/sparql")

        expected_result_df = pd.DataFrame({
            "label": ["Marie Curie, née Sklodowska", "Donna Strickland", "Maria Goeppert Mayer"],
            })

        result = NoblePrize.query(query)

        pd.testing.assert_frame_equal(result, expected_result_df)   



class TestLocalEndpointQuerying:

    def test1_nobleprize_nt(self):

        query = "PREFIX nobel: <http://data.nobelprize.org/terms/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?label WHERE { ?laur rdf:type nobel:Laureate . ?laur rdfs:label ?label . ?laur foaf:gender \"female\" . ?laur nobel:laureateAward ?award . ?award nobel:category <http://data.nobelprize.org/resource/category/Physics> . }"

        path = "test/data/sparql_helper/nobelprize_dump.nt"

        NoblePrize = LocalEndpoint(path, "nt")

        NoblePrize.initialize()

        result = NoblePrize.query(query).sort_values(by=["label"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "label": ["Marie Curie, née Sklodowska", "Donna Strickland", "Maria Goeppert Mayer"],
            }).sort_values(by=["label"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test2_nobleprize_nt_auto(self):

        query = "PREFIX nobel: <http://data.nobelprize.org/terms/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?label WHERE { ?laur rdf:type nobel:Laureate . ?laur rdfs:label ?label . ?laur foaf:gender \"female\" . ?laur nobel:laureateAward ?award . ?award nobel:category <http://data.nobelprize.org/resource/category/Physics> . }"

        path = "test/data/sparql_helper/nobelprize_dump.nt"

        NoblePrize = LocalEndpoint(path)

        NoblePrize.initialize()

        result = NoblePrize.query(query).sort_values(by=["label"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "label": ["Marie Curie, née Sklodowska", "Donna Strickland", "Maria Goeppert Mayer"],
            }).sort_values(by=["label"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result_df.reset_index(drop=True), check_like=True)


    def test3_sparqlplayground_ttl(self):

        query = "select ?person ?pet where {?person rdf:type dbo:Person . ?person tto:pet ?pet .}"

        path = "test/data/sparql_helper/sparqlplayground.ttl"

        SparqlPlayground = LocalEndpoint(path, "ttl")

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["person"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "person": ["http://example.org/tuto/resource#William", "http://example.org/tuto/resource#John", "http://example.org/tuto/resource#John"],
            "pet": ["http://example.org/tuto/resource#RexDog", "http://example.org/tuto/resource#LunaCat", "http://example.org/tuto/resource#TomCat"]
            }).sort_values(by=["person"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test4_sparqlplayground_ttl_auto(self):

        query = "select ?person ?pet where {?person rdf:type dbo:Person . ?person tto:pet ?pet .}"

        path = "test/data/sparql_helper/sparqlplayground.ttl"

        SparqlPlayground = LocalEndpoint(path)

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["person"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "person": ["http://example.org/tuto/resource#William", "http://example.org/tuto/resource#John", "http://example.org/tuto/resource#John"],
            "pet": ["http://example.org/tuto/resource#RexDog", "http://example.org/tuto/resource#LunaCat", "http://example.org/tuto/resource#TomCat"]
            }).sort_values(by=["person"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test5_wikidata_n3(self):

        query = "SELECT ?p ?o WHERE {<https://en.wikiquote.org/wiki/Douglas_Adams> ?p ?o .}"

        path = "test/data/sparql_helper/Q42.n3"

        SparqlPlayground = LocalEndpoint(path, "n3")

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["p"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "p": ["http://schema.org/inLanguage", "http://schema.org/isPartOf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://schema.org/name", "http://schema.org/about"],
            "o": ["en", "https://en.wikiquote.org/", "http://schema.org/Article", "Douglas Adams", "http://www.wikidata.org/entity/Q42"]
            }).sort_values(by=["p"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test6_wikidata_n3_auto(self):

        query = "SELECT ?p ?o WHERE {<https://en.wikiquote.org/wiki/Douglas_Adams> ?p ?o .}"

        path = "test/data/sparql_helper/Q42.n3"

        SparqlPlayground = LocalEndpoint(path)

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["p"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "p": ["http://schema.org/inLanguage", "http://schema.org/isPartOf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://schema.org/name", "http://schema.org/about"],
            "o": ["en", "https://en.wikiquote.org/", "http://schema.org/Article", "Douglas Adams", "http://www.wikidata.org/entity/Q42"]
            }).sort_values(by=["p"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test7_mondialeurope_rdf(self):

        query = """prefix : <http://www.semwebtech.org/mondial/10/meta#>
                SELECT ?N1 ?N2
                WHERE {
                ?X1 a :Country; :capital ?Y1 .
                ?Y1 :name ?N1; :latitude ?lat1; :longitude ?long1 .
                ?X2 a :Country; :capital ?Y2 .
                ?Y2 :name ?N2; :latitude ?lat2; :longitude ?long2 .
                FILTER (?N1 < ?N2)
                Filter (?N1 = "Vaduz")
                }"""

        path = "test/data/sparql_helper/mondial-europe.rdf"

        SparqlPlayground = LocalEndpoint(path, "xml")

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["N2"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "N1": ["Vaduz","Vaduz","Vaduz","Vaduz","Vaduz","Vaduz"],
            "N2": ["Vatican City","Vilnius","Zagreb","Wien","Warszawa","Valletta"]
            }).sort_values(by=["N2"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)


    def test8_mondialeurope_rdf_auto(self):

        query = """prefix : <http://www.semwebtech.org/mondial/10/meta#>
                SELECT ?N1 ?N2
                WHERE {
                ?X1 a :Country; :capital ?Y1 .
                ?Y1 :name ?N1; :latitude ?lat1; :longitude ?long1 .
                ?X2 a :Country; :capital ?Y2 .
                ?Y2 :name ?N2; :latitude ?lat2; :longitude ?long2 .
                FILTER (?N1 < ?N2)
                Filter (?N1 = "Vaduz")
                }"""

        path = "test/data/sparql_helper/mondial-europe.rdf"

        SparqlPlayground = LocalEndpoint(path)

        SparqlPlayground.initialize()

        result = SparqlPlayground.query(query).sort_values(by=["N2"]).reset_index(drop=True)

        expected_result_df = pd.DataFrame({
            "N1": ["Vaduz","Vaduz","Vaduz","Vaduz","Vaduz","Vaduz"],
            "N2": ["Vatican City","Vilnius","Zagreb","Wien","Warszawa","Valletta"]
            }).sort_values(by=["N2"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test9_wrongpath(self):
        
        with pytest.raises(FileNotFoundError):
            path = "test/data/sparql_helper/sparqlplaygroundWRONG.ttl"

            SparqlPlayground = LocalEndpoint(path)

            SparqlPlayground.initialize()

    def test10_brokenquery(self):

        with pytest.raises(pyparsing.ParseException):
            path = "test/data/sparql_helper/sparqlplayground.ttl"

            SparqlPlayground = LocalEndpoint(path)

            SparqlPlayground.initialize()

            SparqlPlayground.query("SELECT *")

    def test11_wrongfile(self):

        with pytest.raises(xml.sax.SAXParseException):
            path = "test/data/sparql_helper/file.random"

            SparqlPlayground = LocalEndpoint(path)

            SparqlPlayground.initialize()


class TestRegexStringGenerator:

    def test1(self):
        
        assert regex_string_generator("?type", ["[^i*&2@]"]) == "regex(?type, \"[^i*&2@]\")"

    def test2(self):
        
        assert regex_string_generator("?type", ["[2-9]|[12]\\d|3[0-6]","^dog","b[aeiou]bble"]) == "regex(?type, \"[2-9]|[12]\\d|3[0-6]\") || regex(?type, \"^dog\") || regex(?type, \"b[aeiou]bble\")"

    def test3_and(self):
        
        assert regex_string_generator("?type", ["[^i*&2@]"], "AND") == "regex(?type, \"[^i*&2@]\")"

    def test4_and(self):
        
        assert regex_string_generator("?type", ["[2-9]|[12]\\d|3[0-6]","^dog","b[aeiou]bble"], "AND") == "regex(?type, \"[2-9]|[12]\\d|3[0-6]\") && regex(?type, \"^dog\") && regex(?type, \"b[aeiou]bble\")"

    def test5_wrongconnector(self):
        
        with pytest.raises(ValueError):
            regex_string_generator("?type", ["[^i*&2@]"], "NOR")

class TestEndpointWrapper:

    def test1_pagesize(self):

        dbpedia = RemoteEndpoint("http://dbpedia.org/sparql/", page_size=1)
        query = "SELECT DISTINCT ?uri WHERE { ?uri rdfs:label ?label . filter(?label =\"Bayern\"@en)}"

        expected_result = pd.DataFrame({
            "uri": ["http://dbpedia.org/resource/Bayern",
            "http://www.wikidata.org/entity/Q255654",
            "http://www.wikidata.org/entity/Q4874432",
            "http://www.wikidata.org/entity/Q18148056"],
            })

        result = endpoint_wrapper(query, dbpedia)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
        
    def test2_timeout_nocache(self):

        dbpedia = RemoteEndpoint("http://dbpedia.org/sparql/", timeout=1, retries=0)
        query = "SELECT ?label ?uri WHERE { ?uri rdfs:label ?label . filter (str(?label) =\"test\")}"
        
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        endpoint_wrapper(query, dbpedia, caching=False)

        assert capturedOutput.getvalue() == 'timed out\n'

    def test3_retries(self):

        dbpedia = RemoteEndpoint("http://dbpedia.org/sparql/", retries=3)

        query = "SELECT DISTINCT ?uri WHERE { ?uri rdfs:label ?label . filter(?label =\"Bayern\"@en)}"

        expected_result = pd.DataFrame({
            "uri": ["http://dbpedia.org/resource/Bayern",
            "http://www.wikidata.org/entity/Q255654",
            "http://www.wikidata.org/entity/Q4874432",
            "http://www.wikidata.org/entity/Q18148056"],
            })

        result = endpoint_wrapper(query, dbpedia)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

    def test4_initial_offset_nocache(self):

        dbpedia = RemoteEndpoint("http://dbpedia.org/sparql/",page_size=1)

        query = "SELECT DISTINCT ?uri WHERE { ?uri rdfs:label ?label . filter(?label =\"Bayern\"@en)} LIMIT 1 OFFSET 2"

        expected_result = pd.DataFrame({
            "uri": ["http://www.wikidata.org/entity/Q4874432"]
            })

        result = endpoint_wrapper(query, dbpedia, caching=True)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

    def test5_wrong_endpointtype(self):
        
        with pytest.raises(TypeError):
            endpoint_wrapper("test_query", "http://dbpedia.org/sparql/")

    def test6_prefix_lookup_true(self):

        query = "SELECT DISTINCT ?name WHERE {<http://dbpedia.org/resource/Bavaria> dbp:name ?name }"

        expected_result = pd.DataFrame({
            "name": ["Free State of Bavaria"]
            })

        result = endpoint_wrapper(query, DBpedia, prefix_lookup=True)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

    def test7_prefix_lookup_json(self):

        query = "SELECT DISTINCT ?homepage WHERE {<http://dbpedia.org/resource/Michael_Wendler> der-wendler:homepage ?homepage }"

        expected_result = pd.DataFrame({
            "homepage": ["http://www.michaelwendler.de/"]
            })

        result = endpoint_wrapper(query, DBpedia, prefix_lookup="test/data/sparql_helper/prefixes_test7.json")

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

    def test8_prefix_lookup_dict(self):

        prefix_dict = {"someprefix": "http://www.w3.org/2000/01/rdf-schema#"}
        query = "SELECT DISTINCT ?we_need WHERE {<http://dbpedia.org/resource/Beer> someprefix:label ?we_need}"

        expected_result = pd.DataFrame({
            "we_need": ['Bier',
                    'ビール',
                    'Beer',
                    'جعة',
                    'Cerveza',
                    'Bière',
                    'Birra',
                    'Bier',
                    'Piwo',
                    'Cerveja',
                    'Пиво',
                    '啤酒']
            })

        result = endpoint_wrapper(query, DBpedia, prefix_lookup=prefix_dict)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

 