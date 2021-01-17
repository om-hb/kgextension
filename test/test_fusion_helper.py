import numpy as np
import pandas as pd
import pytest
from kgextension.fusion_helper import first, last, longest, shortest, voting, provenance


class TestFirst:
    def test1_default(self):
        df_input = pd.DataFrame({
            'a': ['ha', 'us', 'fr', 'au'],
            'b': ['ch', 'ar', 'ma', 'nt']
        })

        df_expected = pd.DataFrame({
            'fused': ['ha', 'us', 'fr', 'au']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(first, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

    def test2_nan(self):
        df_input = pd.DataFrame({
            'a': [np.nan, 3, np.nan, 'au'],
            'b': [np.nan, np.nan, 'Choco', 'nt']
        })

        df_expected = pd.DataFrame({
            'fused': [np.nan, 3, 'Choco', 'au']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(first, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

class TestLast:
    def test1_default(self):
        df_input = pd.DataFrame({
            'a': ['ha', 'us', 'fr', 'au'],
            'b': ['ch', 'ar', 'ma', 'nt']
        })

        df_expected = pd.DataFrame({
            'fused': ['ch', 'ar', 'ma', 'nt']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(last, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

    def test2_nan(self):
        df_input = pd.DataFrame({
            'a': [np.nan, 3, np.nan, 'au'],
            'b': [np.nan, np.nan, 'Choco', 'nt']
        })

        df_expected = pd.DataFrame({
            'fused': [np.nan, 3, 'Choco', 'nt']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(last, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

class TestLongest:
    def test1_default(self):
        df_input = pd.DataFrame({
            'a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'b': ['chicoree', 'arm', 'mantra', 'mantel']
        })

        df_expected = pd.DataFrame({
            'fused': ['chicoree', 'usa', 'frauenkirche', 'mantel']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(longest, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

    def test2_nan(self):
        df_input = pd.DataFrame({
            'a': [np.nan, 'usa', np.nan, 'aua'],
            'b': [np.nan, np.nan, 'mantra', 'mantel']
        })

        df_expected = pd.DataFrame({
            'fused': [np.nan, 'usa', 'mantra', 'mantel']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(longest, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

class TestShortest:
    def test1_default(self):
        df_input = pd.DataFrame({
            'a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'b': ['chicoree', 'arm', 'mantra', 'mantel']
        })

        df_expected = pd.DataFrame({
            'fused': ['haus', 'usa', 'mantra', 'aua']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(shortest, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

    def test2_nan(self):
        df_input = pd.DataFrame({
            'a': [np.nan, 'usa', np.nan, 'aua'],
            'b': [np.nan, np.nan, 'mantra', 'mantel']
        })

        df_expected = pd.DataFrame({
            'fused': [np.nan, 'usa', 'mantra', 'aua']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(shortest, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

class TestVoting:
    def test1_default(self):
        df_input = pd.DataFrame({
            'a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'b': ['chicoree', 'usa', 'mantra', 'mantel'],
            'c': ['haus', True, 'mantra', 'sonnengruss']
        })

        df_expected = pd.DataFrame({
            'fused': ['haus', 'usa', 'mantra', 'aua']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(voting, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

    def test2_nan(self):
        df_input = pd.DataFrame({
            'a': ['haus', 'usa', np.nan, np.nan],
            'b': ['chicoree', 'usa', np.nan, 'mantel'],
            'c': ['haus', np.nan, np.nan, 'sonnengruss']
        })

        df_expected = pd.DataFrame({
            'fused': ['haus', 'usa', np.nan, 'mantel']
        })

        output = pd.DataFrame({'fused': [0, 0, 0, 0]})
        output['fused'] = df_input.apply(voting, axis=1)

        pd.testing.assert_frame_equal(
            output, df_expected)

class TestProvenance:
    def test1_default(self):
        columns_input = pd.DataFrame({
            'www.test_spass.de/a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'http://dbpedia.org//b': ['chicoree', 'usa', 'mantra', 'mantel'],
            'www.test_ernst.de/c': ['haus', True, 'mantra', 'sonnengruss']
        }).columns

        output = provenance(columns_input)

        assert output == 'http://dbpedia.org//b'

    def test2_nan(self):
        columns_input = pd.DataFrame({
            np.nan: ['haus', 'usa', 'frauenkirche', 'aua'],
            'http://dbpedia.org//b': ['chicoree', 'usa', 'mantra', 'mantel'],
            'www.test_ernst.de/c': ['haus', True, 'mantra', 'sonnengruss']
        }).columns

        output = provenance(columns_input)

        assert output == 'http://dbpedia.org//b'

    def test3_no_match(self):
        columns_input = pd.DataFrame({
            'www.test_spass.de/a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'http://dbpedia.org//b': ['chicoree', 'usa', 'mantra', 'mantel'],
            'www.test_ernst.de/c': ['haus', True, 'mantra', 'sonnengruss']
        }).columns

        with pytest.raises(RuntimeError) as excinfo:
            _ = provenance(columns_input, regex = 'bananaboat')

        assert "No column satisfies the regex." in str(excinfo.value)

    def test4_multiple_matches(self):
        columns_input = pd.DataFrame({
            'www.bananaboat.de/a': ['haus', 'usa', 'frauenkirche', 'aua'],
            'http://dbpedia.org//b': ['chicoree', 'usa', 'mantra', 'mantel'],
            'www.test_ernst.bananaboat/c': ['haus', True, 'mantra', 'sonnengruss']
        }).columns

        with pytest.raises(RuntimeError) as excinfo:
            _ = provenance(columns_input, regex = 'bananaboat')

        assert "More than one of the matches" in str(excinfo.value)
