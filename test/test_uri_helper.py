from kgextension.uri_helper import query_uri, uri_querier
import pytest
import pandas as pd
import numpy as np

class TestQueryUri:

    def test1_missinguri(self):
        
        uri = np.nan
        query_string = """SELECT *
                        WHERE {
                        VALUES ?value {<http://dbpedia.org/resource/Michael_Ballack__2>}
                        ?value rdf:type ?o .}"""

        expected_result_df = pd.DataFrame()

        result = query_uri(uri, query_string)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test2_brokenuri(self):
        
        uri = "https://www.dd"
        query_string = """SELECT *
                        WHERE {
                        VALUES ?value {<http://dbpedia.org/resource/Michael_Ballack__2>}
                        ?value rdf:type ?o .}"""


        expected_result_df = pd.DataFrame()

        with pytest.warns(UserWarning) as record:
            result = query_uri(uri, query_string)

        assert len(record) == 1
        assert record[0].message.args[0] == "https://www.dd is not a valid URI."

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test3_wronglyformatteduri(self):
        
        uri = "www.google.de"
        query_string = """SELECT *
                        WHERE {
                        VALUES ?value {<http://dbpedia.org/resource/Michael_Ballack__2>}
                        ?value rdf:type ?o .}"""


        expected_result_df = pd.DataFrame()

        with pytest.warns(UserWarning) as record:
            result = query_uri(uri, query_string)

        assert len(record) == 1
        assert record[0].message.args[0] == "www.google.de might not be a valid URI."

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test4_notdereferencableuri(self):
        
        uri = "https://www.google.de"
        query_string = """SELECT *
                        WHERE {
                        VALUES ?value {<http://dbpedia.org/resource/Michael_Ballack__2>}
                        ?value rdf:type ?o .}"""
        
        expected_result_df = pd.DataFrame()

        with pytest.warns(UserWarning) as record:
            result = query_uri(uri, query_string)

        assert len(record) == 1
        assert record[0].message.args[0] == "https://www.google.de might not be dereferencable."

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test5_dbpedia(self):
        
        uri = "http://dbpedia.org/resource/Michael_Ballack__2"
        query_string = """SELECT *
                        WHERE {
                        VALUES ?value {<http://dbpedia.org/resource/Michael_Ballack__2>}
                        ?value rdf:type ?o .}"""

        expected_result_df = pd.DataFrame({
            "value": ["http://dbpedia.org/resource/Michael_Ballack__2", "http://dbpedia.org/resource/Michael_Ballack__2", "http://dbpedia.org/resource/Michael_Ballack__2"],
            "o": ["http://dbpedia.org/ontology/CareerStation", "http://dbpedia.org/ontology/TimePeriod", "http://www.w3.org/2002/07/owl#Thing"]
            })

        result = query_uri(uri, query_string)

        pd.testing.assert_frame_equal(result.sort_values("o", ignore_index=True), expected_result_df.sort_values("o", ignore_index=True), check_like = True)

    def test6_wikidata(self):
        
        uri = "http://www.wikidata.org/entity/Q937"
        query_string = "SELECT ?cc WHERE {VALUES ?value {<http://www.wikidata.org/entity/Q937>} ?value wdt:P27 ?cc .}"

        expected_result_df = pd.DataFrame({'cc': ["http://www.wikidata.org/entity/Q30", "http://www.wikidata.org/entity/Q39", "http://www.wikidata.org/entity/Q28513", "http://www.wikidata.org/entity/Q41304", "http://www.wikidata.org/entity/Q43287"]})

        result = query_uri(uri, query_string)

        pd.testing.assert_frame_equal(result.sort_values("cc", ignore_index=True), expected_result_df.sort_values("cc", ignore_index=True), check_like = True)

    def test7_eurostat(self):
        
        uri= "http://publications.europa.eu/resource/authority/corporate-body/ESTAT"
        query_string = query_string = "PREFIX dcat: <http://www.w3.org/ns/dcat#> PREFIX odp: <http://data.europa.eu/euodp/ontologies/ec-odp#> PREFIX dc: <http://purl.org/dc/terms/> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT * WHERE {VALUES ?value {<http://publications.europa.eu/resource/authority/corporate-body/ESTAT>} ?value skos:broader ?o.}"

        expected_result_df = pd.DataFrame({"value": ["http://publications.europa.eu/resource/authority/corporate-body/ESTAT"],
            "o": ["http://publications.europa.eu/resource/authority/corporate-body/COM"]})

        result = query_uri(uri, query_string)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)



class TestUriQuerier:

    def test1(self):

        # Not all attributes (here "adresse") are present for all of the URIs.

        input = pd.DataFrame(
            {'uris': ['http://dbpedia.org/resource/Berlin',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/London',
                        'http://dbpedia.org/resource/Munich']})

        query = "SELECT DISTINCT ?uri ?adresse ?lat WHERE {VALUES (?uri) {(<**URI**>)} ?uri dbp:adresse ?adresse. ?uri geo:lat ?lat} ORDER BY ?adresse LIMIT 2"

        result = uri_querier(input, "uris", query)

        expected_result_df = pd.DataFrame(
            {'uri': ['http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Munich',
                        'http://dbpedia.org/resource/Munich'],
            'adresse': ['Luisenplatz 5', '64283', 'Marienplatz 8', '80331'],
            'lat': [49.8667, 49.8667, 48.1333, 48.1333]})

        pd.testing.assert_frame_equal(result, expected_result_df, check_like=True)


    def test2_noprogressbar(self):

        # Not all attributes (here "adresse") are present for all of the URIs.

        input = pd.DataFrame(
            {'uris': ['http://dbpedia.org/resource/Berlin',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/London',
                        'http://dbpedia.org/resource/Munich']})

        query = "SELECT DISTINCT ?uri ?adresse ?lat WHERE {VALUES (?uri) {(<**URI**>)} ?uri dbp:adresse ?adresse. ?uri geo:lat ?lat} ORDER BY ?adresse LIMIT 2"

        result = uri_querier(input, "uris", query, progress=False)

        expected_result_df = pd.DataFrame(
            {'uri': ['http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Munich',
                        'http://dbpedia.org/resource/Munich'],
            'adresse': ['Luisenplatz 5', '64283', 'Marienplatz 8', '80331'],
            'lat': [49.8667, 49.8667, 48.1333, 48.1333]})

        pd.testing.assert_frame_equal(result, expected_result_df, check_like=True)


    def test3_nocaching(self):

        # Not all attributes (here "adresse") are present for all of the URIs.

        input = pd.DataFrame(
            {'uris': ['http://dbpedia.org/resource/Berlin',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/London',
                        'http://dbpedia.org/resource/Munich']})

        query = "SELECT DISTINCT ?uri ?adresse ?lat WHERE {VALUES (?uri) {(<**URI**>)} ?uri dbp:adresse ?adresse. ?uri geo:lat ?lat} ORDER BY ?adresse LIMIT 2"

        result = uri_querier(input, "uris", query, caching=False)

        expected_result_df = pd.DataFrame(
            {'uri': ['http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Darmstadt',
                        'http://dbpedia.org/resource/Munich',
                        'http://dbpedia.org/resource/Munich'],
            'adresse': ['Luisenplatz 5', '64283', 'Marienplatz 8', '80331'],
            'lat': [49.8667, 49.8667, 48.1333, 48.1333]})

        pd.testing.assert_frame_equal(result, expected_result_df, check_like=True)


    def test4_brokenuris(self):

        # Not all attributes (here "adresse") are present for all of the URIs.

        input = pd.DataFrame(
            {'uris': ['https://www.dd',
                        'www.google.de',
                        'https://www.google.de',
                        'http://dbpedia.org/resource/Munich',
                        np.nan]})

        query = "SELECT DISTINCT ?uri ?adresse ?lat WHERE {VALUES (?uri) {(<**URI**>)} ?uri dbp:adresse ?adresse. ?uri geo:lat ?lat} ORDER BY ?adresse LIMIT 2"

        with pytest.warns(UserWarning) as record:
            result = uri_querier(input, "uris", query, progress=True)

        assert len(record) == 3
        assert record[0].message.args[0] == "https://www.dd is not a valid URI."
        assert record[1].message.args[0] == "www.google.de might not be a valid URI."
        assert record[2].message.args[0] == "https://www.google.de might not be dereferencable."

        expected_result_df = pd.DataFrame(
            {'uri': ['http://dbpedia.org/resource/Munich',
                    'http://dbpedia.org/resource/Munich'],
            'adresse': ['Marienplatz 8', '80331'],
            'lat': [48.1333, 48.1333]})

        pd.testing.assert_frame_equal(result, expected_result_df, check_like=True)

