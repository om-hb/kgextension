import pytest
import unittest
import numpy as np
import pandas as pd
from kgextension.endpoints import EUOpenData, DBpedia, WikiData
from kgextension.linking import sameas_linker
from kgextension.linking import dbpedia_spotlight_linker
from kgextension.linking import label_linker
from kgextension.linking import dbpedia_lookup_linker
from kgextension.linking import pattern_linker
import sys


class TestPatternLinker(unittest.TestCase):

    def test1(self):
        input_ = pd.DataFrame(
            {'test_col': ['Scotland', 'Northern Ireland',
                          'Greater London', 'East Midlands']})
        expected = pd.DataFrame(
            {'test_col': ['Scotland', 'Northern Ireland',
                          'Greater London', 'East Midlands'],
             'new_link': ['www.dbpedia.org/resource/Scotland',
                          'www.dbpedia.org/resource/Northern_Ireland',
                          'www.dbpedia.org/resource/Greater_London',
                          'www.dbpedia.org/resource/East_Midlands']})
        output = pattern_linker(
            input_, 'test_col', 'www.dbpedia.org/resource/')
        self.assertTrue(output.equals(
            expected), "The 'new_link' column should return the expected DBpedia link")


class TestSpotlightLinker():

    def test1_default(self):
        input_ = pd.DataFrame(
            {'test_col': ['berlin', 'darmstadt',
                          'london', 'munich']})
        expected = pd.DataFrame(
            {'test_col': ['berlin', 'darmstadt',
                          'london', 'munich'],
             'new_link': ['http://dbpedia.org/resource/Berlin',
                          'http://dbpedia.org/resource/Darmstadt',
                          'http://dbpedia.org/resource/London',
                          'http://dbpedia.org/resource/Munich']})
        output = dbpedia_spotlight_linker(input_, 'test_col')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test2_5_hits(self):
        input_ = pd.DataFrame(
            {'test_col': ['berlin and paris are both capitals', 
                          'Angela M. plans to buy a flat in Hamburg',
                          'The BASF is located in Ludwigshafen, Rhineland-Palatine', 
                          'Crist. Ronaldo plays in Madrid for Real Madrid']})

        expected = pd.read_csv("test/data/linking/5hits_expected.csv")
        output = dbpedia_spotlight_linker(input_, 'test_col', max_hits=5)

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test3_nan(self):
        input_ = pd.DataFrame(
            {'test_col': ['Dakar', 'Horse Racing in Uruguay',
                           np.nan, 'Ukulele']})
        expected = pd.DataFrame(
            {'test_col': ['Dakar', 'Horse Racing in Uruguay',
                           np.nan, 'Ukulele'],
             'new_link': ['http://dbpedia.org/resource/Dakar',
                          'http://dbpedia.org/resource/Horse_racing',
                           np.nan,
                          'http://dbpedia.org/resource/Ukulele']})
        output = dbpedia_spotlight_linker(input_, 'test_col')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test4_selection_support(self):
        input_ = pd.DataFrame(
            {'test_col': ['Berlin and Paris are both capitals but Paris is rich and Paris is in France', 
                          'Rather Rome or Madrid? Definitely Rome!',
                          'Hamburg? Hamburg is not a city in Rhineland-Palatine', 
                          "If I had to choose between Spaghetti or Linguine I'd always choose Spaghetti"]})
        expected = pd.DataFrame(
            {'test_col': ['Berlin and Paris are both capitals but Paris is rich and Paris is in France', 
                          'Rather Rome or Madrid? Definitely Rome!',
                          'Hamburg? Hamburg is not a city in Rhineland-Palatine', 
                          "If I had to choose between Spaghetti or Linguine I'd always choose Spaghetti"],
             'new_link': ['http://dbpedia.org/resource/France',
                          'http://dbpedia.org/resource/Rome',
                           'http://dbpedia.org/resource/Hamburg',
                          'http://dbpedia.org/resource/Spaghetti']})

        output = dbpedia_spotlight_linker(input_, 'test_col', selection='support')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test5_selection_similarityScore(self):
        input_ = pd.DataFrame(
            {'test_col': ['Berlin and Paaris? Berlin and Pariss!', 
                          'Foooootball or Rugbyy?',
                          'How to write New Yorrk? or is it Neew York', 
                          "Hopelessly trying to spell Emannuel Makrone"]})

        expected = pd.DataFrame(
            {'test_col': ['Berlin and Paaris? Berlin and Pariss!', 
                          'Foooootball or Rugbyy?',
                          'How to write New Yorrk? or is it Neew York', 
                          "Hopelessly trying to spell Emannuel Makrone"],
             'new_link': ['http://dbpedia.org/resource/Berlin',
                           np.nan,
                          'http://dbpedia.org/resource/How_(TV_series)',
                          'http://dbpedia.org/resource/Hopelessly']})
        output = dbpedia_spotlight_linker(input_, 'test_col', 
            selection='similarityScore')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test6_high_confidence(self):
        input_ = pd.DataFrame(
            {'test_col': ['Barack Hussein Obama', 'Barrrack Obbama',
                          'President B. Obama', 'B. Obama']})

        expected = pd.DataFrame(
            {'test_col': ['Barack Hussein Obama', 'Barrrack Obbama',
                          'President B. Obama', 'B. Obama'],
             'new_link': ['http://dbpedia.org/resource/Barack_Obama',
                           np.nan, np.nan, np.nan]})
        output = dbpedia_spotlight_linker(input_, 'test_col', 
            confidence=0.99)

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test7_no_match(self):
        input_ = pd.DataFrame(
            {'test_col': ['B. Obama', 'Barrrack Obbama',
                          'President B. Obama', 'B. Obama']})

        expected = pd.DataFrame(
            {'test_col': ['B. Obama', 'Barrrack Obbama',
                          'President B. Obama', 'B. Obama'],
             'new_link': [np.nan, np.nan, np.nan, np.nan]})
             
        output = dbpedia_spotlight_linker(input_, 'test_col', 
            confidence=0.99)

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test8_all_nan(self):
        input_ = pd.DataFrame(
            {'test_col': [np.nan, np.nan,
                          np.nan, np.nan]})

        expected = pd.DataFrame(
            {'test_col': [np.nan, np.nan, np.nan, np.nan],
             'new_link': [np.nan, np.nan, np.nan, np.nan]})
             
        output = dbpedia_spotlight_linker(input_, 'test_col')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)

    def test9_wrong_input_type(self):
        input_ = pd.DataFrame(
            {'test_col': ['B. Obama', 666,
                          'President B. Obama', 'B. Obama']})

        expected = pd.DataFrame(
            {'test_col': ['B. Obama', 666,
                          'President B. Obama', 'B. Obama'],
             'new_link': ['http://dbpedia.org/resource/Barack_Obama', 
                np.nan, 'http://dbpedia.org/resource/President_of_the_United_States', 
                'http://dbpedia.org/resource/Barack_Obama']})
             
        output = dbpedia_spotlight_linker(input_, 'test_col')

        pd.testing.assert_frame_equal(
                output, expected, check_like=True)


class TestLookupLinker:

    def test1_default(self):

        df = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan]})

        df_expected_results = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan],
            "new_link": ["http://dbpedia.org/resource/Germany", "http://dbpedia.org/resource/Italy", "http://dbpedia.org/resource/United_States", "http://dbpedia.org/resource/Italy", np.nan, np.nan]
        })

        df_result = dbpedia_lookup_linker(
            df, "term", new_attribute_name="new_link", query_class="", max_hits=1, lookup_api="KeywordSearch")

        pd.testing.assert_frame_equal(
            df_result, df_expected_results, check_like=True)

    def test2_multiplehits(self):

        df = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", "dsajiasjdijasidojasiopdsapo"]})

        df_expected_results = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", "dsajiasjdijasidojasiopdsapo"],
            "new_link_1": ["http://dbpedia.org/resource/Germany", "http://dbpedia.org/resource/Italy", "http://dbpedia.org/resource/United_States", "http://dbpedia.org/resource/Italy", np.nan, np.nan],
            "new_link_2": ["http://dbpedia.org/resource/West_Germany", "http://dbpedia.org/resource/Kingdom_of_Italy", "http://dbpedia.org/resource/Democratic_Party_(United_States)", "http://dbpedia.org/resource/Kingdom_of_Italy", np.nan, np.nan],
            "new_link_3": ["http://dbpedia.org/resource/Nazi_Germany", "http://dbpedia.org/resource/Italy_national_football_team", "http://dbpedia.org/resource/California", "http://dbpedia.org/resource/Italy_national_football_team", np.nan, np.nan],
            "new_link_4": ["http://dbpedia.org/resource/East_Germany", "http://dbpedia.org/resource/Cinema_of_Italy", "http://dbpedia.org/resource/Republican_Party_(United_States)", "http://dbpedia.org/resource/Cinema_of_Italy", np.nan, np.nan],
            "new_link_5": ["http://dbpedia.org/resource/Germany_national_football_team", "http://dbpedia.org/resource/Italy_national_under-21_football_team", "http://dbpedia.org/resource/Americans", "http://dbpedia.org/resource/Italy_national_under-21_football_team", np.nan, np.nan]
        })

        df_result = dbpedia_lookup_linker(
            df, "term", new_attribute_name="new_link", query_class="", max_hits=5, lookup_api="KeywordSearch")

        pd.testing.assert_frame_equal(
            df_result, df_expected_results, check_like=True)

    def test3_multiplehits_classfilter(self):

        df = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan]})

        df_expected_results = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan],
            "new_link_1": ["http://dbpedia.org/resource/Germany", "http://dbpedia.org/resource/Italy", "http://dbpedia.org/resource/United_States", "http://dbpedia.org/resource/Italy", np.nan, np.nan],
            "new_link_2": ["http://dbpedia.org/resource/Berlin", "http://dbpedia.org/resource/Rome", "http://dbpedia.org/resource/National_Academy_of_Sciences", "http://dbpedia.org/resource/Rome", np.nan, np.nan],
            "new_link_3": ["http://dbpedia.org/resource/Nazi_Germany", "http://dbpedia.org/resource/Milan", "http://dbpedia.org/resource/United_States_Capitol", "http://dbpedia.org/resource/Milan", np.nan, np.nan],
            "new_link_4": ["http://dbpedia.org/resource/Munich", "http://dbpedia.org/resource/Venice", "http://dbpedia.org/resource/Southeastern_United_States", "http://dbpedia.org/resource/Venice", np.nan, np.nan],
            "new_link_5": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Florence", "http://dbpedia.org/resource/M-55_(Michigan_highway)", "http://dbpedia.org/resource/Florence", np.nan, np.nan]
        })

        df_result = dbpedia_lookup_linker(
            df, "term", new_attribute_name="new_link", query_class="place", max_hits=5, lookup_api="KeywordSearch")

        pd.testing.assert_frame_equal(
            df_result, df_expected_results, check_like=True)

    def test4_multiplehits_classfilter_falseclass(self):

        df = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan]})

        df_expected_results = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan], 
            "new_link": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]})

        df_result = dbpedia_lookup_linker(
            df, "term", new_attribute_name="new_link", query_class="ABCD", max_hits=5, lookup_api="KeywordSearch")

        pd.testing.assert_frame_equal(
            df_result, df_expected_results, check_like=True)

    def test5_lookupapi(self):

        df = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan]})

        df_expected_results = pd.DataFrame({
            "term": ["Germany", "Italy", "United States of America", "Italy", "", np.nan],
            "new_link": ["http://dbpedia.org/resource/Germany", "http://dbpedia.org/resource/Italy", "http://dbpedia.org/resource/United_States", "http://dbpedia.org/resource/Italy", np.nan, np.nan]
        })

        df_result = dbpedia_lookup_linker(
            df, "term", new_attribute_name="new_link", query_class="", max_hits=1, lookup_api="PrefixSearch")

        pd.testing.assert_frame_equal(
            df_result, df_expected_results, check_like=True)


class TestSameAsLinker:

    def test1_wikidata_bundled(self):

        df = pd.DataFrame({
            "word": ["they", "they", "she", "she", "he"],
            "uri": ["http://www.wikidata.org/entity/L1372", "http://www.wikidata.org/entity/L493", "http://www.wikidata.org/entity/L1370", "http://www.wikidata.org/entity/L496", "http://www.wikidata.org/entity/L1371"]
        })

        expected_result_df = pd.DataFrame({
            "word": ["they", "they", "she", "she", "he"],
            "uri": ["http://www.wikidata.org/entity/L1372", "http://www.wikidata.org/entity/L493", "http://www.wikidata.org/entity/L1370", "http://www.wikidata.org/entity/L496", "http://www.wikidata.org/entity/L1371"],
            "same_as_1": ["http://www.wikidata.org/entity/L371", "http://www.wikidata.org/entity/L371", "http://www.wikidata.org/entity/L484", "http://www.wikidata.org/entity/L484", "http://www.wikidata.org/entity/L485"]
        })

        result = sameas_linker(df, "uri", new_attribute_name="same_as", endpoint=WikiData, bundled_mode=True)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test2_wikidata_unbundled(self):

        df = pd.DataFrame({
            "word": ["they", "they", "she", "she", "he"],
            "uri": ["http://www.wikidata.org/entity/L1372", "http://www.wikidata.org/entity/L493", "http://www.wikidata.org/entity/L1370", "http://www.wikidata.org/entity/L496", "http://www.wikidata.org/entity/L1371"]
        })

        expected_result_df = pd.DataFrame({
            "word": ["they", "they", "she", "she", "he"],
            "uri": ["http://www.wikidata.org/entity/L1372", "http://www.wikidata.org/entity/L493", "http://www.wikidata.org/entity/L1370", "http://www.wikidata.org/entity/L496", "http://www.wikidata.org/entity/L1371"],
            "same_as_1": ["http://www.wikidata.org/entity/L371", "http://www.wikidata.org/entity/L371", "http://www.wikidata.org/entity/L484", "http://www.wikidata.org/entity/L484", "http://www.wikidata.org/entity/L485"]
        })

        result = sameas_linker(
            df, "uri", new_attribute_name="same_as", endpoint=WikiData, bundled_mode=False)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test3_dbpedia_bundled_filter(self):

        df = pd.DataFrame({
            "label": ["Universität Mannheim", "Universität Bremen"],
            "uri": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Bremen"]
        })

        expected_result_df = pd.DataFrame({
            "label": ["Universität Mannheim", "Universität Bremen"],
            "uri": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Bremen"],
            "same_as_1": ["http://yago-knowledge.org/resource/University_of_Mannheim", "http://yago-knowledge.org/resource/University_of_Bremen"],
            "same_as_2": ["http://rdf.freebase.com/ns/m.0b6dry", "http://rdf.freebase.com/ns/m.04fd75"],
            "same_as_3": ["http://www.wikidata.org/entity/Q317070", "http://www.wikidata.org/entity/Q500692"],
            "same_as_4": ["http://wikidata.dbpedia.org/resource/Q317070", "http://wikidata.dbpedia.org/resource/Q500692"]
        })

        result = sameas_linker(df, "uri", new_attribute_name="same_as", endpoint=DBpedia, result_filter=[
                               "yago", "freebase", "wiki"], bundled_mode=True)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test4_dbpedia_unbundled_filter(self):

        df = pd.DataFrame({
            "label": ["Universität Mannheim", "Universität Bremen"],
            "uri": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Bremen"]
        })

        expected_result_df = pd.DataFrame({
            "label": ["Universität Mannheim", "Universität Bremen"],
            "uri": ["http://dbpedia.org/resource/University_of_Mannheim", "http://dbpedia.org/resource/University_of_Bremen"],
            "same_as_1": ["http://yago-knowledge.org/resource/University_of_Mannheim", "http://yago-knowledge.org/resource/University_of_Bremen"],
            "same_as_2": ["http://rdf.freebase.com/ns/m.0b6dry", "http://rdf.freebase.com/ns/m.04fd75"],
            "same_as_3": ["http://www.wikidata.org/entity/Q317070", "http://www.wikidata.org/entity/Q500692"],
            "same_as_4": ["http://wikidata.dbpedia.org/resource/Q317070", "http://wikidata.dbpedia.org/resource/Q500692"]
        })

        result = sameas_linker(df, "uri", new_attribute_name="same_as", endpoint=DBpedia, result_filter=[
                               "yago", "freebase", "wiki"], bundled_mode=False)

        pd.testing.assert_frame_equal(result, expected_result_df)


class TestLabelLinker:

    def test1_dbpedia_en_gu(self):

        df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"]
        })

        expected_result_df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"],
            "new_link_1": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Bayern", "http://dbpedia.org/resource/Sachsen"]
        })

        result = label_linker(df, "state", endpoint=DBpedia,
                              language="en")

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test2_dbpedia_en(self):

        df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"]
        })

        expected_result_df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"],
            "new_link_1": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Bayern", "http://dbpedia.org/resource/Sachsen"],
            "new_link_2": ["http://www.wikidata.org/entity/Q985", "http://www.wikidata.org/entity/Q255654", "http://www.wikidata.org/entity/Q16882470"],
            "new_link_3": ["http://www.wikidata.org/entity/Q20825585", "http://www.wikidata.org/entity/Q4874432", np.nan],
            "new_link_4": [np.nan, "http://www.wikidata.org/entity/Q18148056", np.nan]
        })

        result = label_linker(df, "state", endpoint=DBpedia, language="en")

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test3_dbpedia_de_gu(self):

        df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"]
        })

        expected_result_df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"],
            "new_link_1": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Bavaria", "http://dbpedia.org/resource/Saxony"]
        })

        result = label_linker(df, "state", endpoint=DBpedia,
                              language="de")

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test4_dbpedia_de(self):

        df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"]
        })

        expected_result_df = pd.DataFrame({
            "state": ["Baden-Württemberg", "Bayern", "Sachsen"],
            "new_link_1": ["http://dbpedia.org/resource/Baden-Württemberg", "http://www.wikidata.org/entity/Q980", "http://dbpedia.org/resource/Saxony"],
            "new_link_2": ["http://www.wikidata.org/entity/Q985", "http://dbpedia.org/resource/Bavaria", "http://www.wikidata.org/entity/Q467095"],
            "new_link_3": ["http://www.wikidata.org/entity/Q21036291", "http://www.wikidata.org/entity/Q255654", "http://www.wikidata.org/entity/Q1202"],
            "new_link_4": [np.nan, "http://www.wikidata.org/entity/Q4874432", "http://www.wikidata.org/entity/Q101985"],
            "new_link_5": [np.nan, "http://www.wikidata.org/entity/Q18148056", "http://www.wikidata.org/entity/Q3873416"],
            "new_link_6": [np.nan, np.nan, "http://www.wikidata.org/entity/Q27505"],
            "new_link_7": [np.nan, np.nan, "http://www.wikidata.org/entity/Q16882470"],
            "new_link_8": [np.nan, np.nan, "http://www.wikidata.org/entity/Q1325543"],
            "new_link_9": [np.nan, np.nan, "http://www.wikidata.org/entity/Q1435378"],
            "new_link_10": [np.nan, np.nan, "http://www.wikidata.org/entity/Q1537344"],
            "new_link_11": [np.nan, np.nan, "http://www.wikidata.org/entity/Q1365112"]
        })

        result = label_linker(df, "state", endpoint=DBpedia, language="de", max_hits=11)

        pd.testing.assert_frame_equal(result, expected_result_df)


if __name__ == '__main__':
    unittest.main()
