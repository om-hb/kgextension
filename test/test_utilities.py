from kgextension.utilities import link_validator, check_uri_redirects
import pandas as pd
import numpy as np
import pytest

class TestLinkValidator:

    def test1_purge(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_result = link_validator(df, ["url"], purge=True)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test2_purge_multicolumn(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_result = link_validator(df, ["url_1","url_2"], purge=True)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test3_notpurge(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_exists": [False,False,True,True,True,False,True,True,False,False]
            })

        df_result = link_validator(df, ["url"], purge=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)



    def test4_notpurge_multicolumn(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_2": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_2": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_1_exists": [False,False,True,True,True,False,True,True,False,False],
            "url_2_exists": [False,False,True,True,True,False,True,True,False,False],
            })

        df_result = link_validator(df, ["url_1","url_2"], purge=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test5_notpurge_multicolumn_postfix(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_2": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_2": ["gist.github.com/sloria/7001839", 
            "https://realpython.com/python-application-layouts/abc", 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            "www.datacamp.com/community/tutorials/docstrings-python",
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            "http://dbpedia.org/page/Baden-WürttembergX",
            ""
            ],
            "url_1_link_check": [False,False,True,True,True,False,True,True,False,False],
            "url_2_link_check": [False,False,True,True,True,False,True,True,False,False],
            })

        df_result = link_validator(df, ["url_1","url_2"], custom_name_postfix="_link_check", purge=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)

    def test6_purge_multicolumn_nocaching(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_result = link_validator(df, ["url_1","url_2"], purge=True, caching=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)

    def test7_purge_multicolumn_nocaching_noprogress(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc", "abc"], 
            "url_1": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ],
            "url_2": [np.nan, 
            np.nan, 
            "https://docs.python-guide.org/writing/structure/",
            "https://docs.pytest.org/en/latest/",
            "https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/",
            np.nan,
            "http://dbpedia.org/page/Baden-Württemberg",
            "http://dbpedia.org/page/Baden-W%C3%BCrttemberg",
            np.nan,
            np.nan
            ]
            })

        df_result = link_validator(df, ["url_1","url_2"], purge=True, caching=False, progress=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


class TestCheckUriRedirects:

    def test1_dbpedia_bundled(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Saxony", 
            "http://dbpedia.org/resource/Hesse",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=True, bundled_mode=True, uri_data_model=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test2_dbpedia_unbundled(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Saxony", 
            "http://dbpedia.org/resource/Hesse",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=True, bundled_mode=False, uri_data_model=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test3_dbpedia_uridatamodel(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Saxony", 
            "http://dbpedia.org/resource/Hesse",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=True, bundled_mode=False, uri_data_model=True)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test4_dbpedia_bundled_noreplace(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan], 
            "url_redirect" : ["http://dbpedia.org/resource/Saxony", 
            "http://dbpedia.org/resource/Hesse",
            np.nan,
            np.nan,
            np.nan,
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=False, bundled_mode=True, uri_data_model=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test5_dbpedia_bundled_noreplace_postfix(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Sachsen", 
            "http://dbpedia.org/resource/Hessen",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan], 
            "url_checked" : ["http://dbpedia.org/resource/Saxony", 
            "http://dbpedia.org/resource/Hesse",
            np.nan,
            np.nan,
            np.nan,
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=False, bundled_mode=True, uri_data_model=False, custom_name_postfix="_checked")

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)


    def test6_dbpedia_noredirects(self):

        df = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Mainz", 
            "http://dbpedia.org/resource/Paris",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_expected_results = pd.DataFrame({
            "random_string": ["abc", "abc", "abc", "abc", "abc", "abc"], 
            "url" : ["http://dbpedia.org/resource/Mainz", 
            "http://dbpedia.org/resource/Paris",
            "http://dbpedia.org/resource/Bremen",
            "http://dbpedia.org/resource/New_York",
            "http://dbpedia.org/resource/New_YorkXXXX",
            np.nan]
            })

        df_result = check_uri_redirects(df, "url", replace=True, bundled_mode=True, uri_data_model=False)

        pd.testing.assert_frame_equal(df_result, df_expected_results, check_like = True)
