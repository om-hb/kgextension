import pandas as pd
import numpy as np
import pytest
from kgextension.caching_helper import freeze_unhashable, unfreeze_unhashable

class TestFreezeUnfreezeUnhashable:

    def test1_arg_series(self):

        @freeze_unhashable(freeze_by="argument", freeze_argument="the_arg")
        def test_fun(a, b, c=12, the_arg=[]):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        df = pd.DataFrame({"a": [1,2,3,np.nan], "b": ["x", "y", "z", np.nan]})

        s = df["a"]

        s_unfrozen = test_fun(10, 11, the_arg=s)

        pd.testing.assert_series_equal(s, s_unfrozen)


    def test2_arg_series_kwargs(self):

        @freeze_unhashable(freeze_by="argument", freeze_argument="the_arg")
        def test_fun(a, b, c=12, the_arg=[]):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        df = pd.DataFrame({"a": [1,2,3,np.nan], "b": ["x", "y", "z", np.nan]})

        s = df["a"]

        s_unfrozen = test_fun(a=10, b=11, the_arg=s)

        pd.testing.assert_series_equal(s, s_unfrozen)


    def test3_arg_series_kwargs_noatttrib(self):

        @freeze_unhashable(freeze_by="argument", freeze_argument="the_arg")
        def test_fun(a=10, b=11, c=12, the_arg=[]):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        s_unfrozen = test_fun(a=10, b=11)

        assert s_unfrozen == []


    def test4_arg_dict(self):

        @freeze_unhashable(freeze_by="argument", freeze_argument="the_arg")
        def test_fun(a, b, c=12, the_arg=[]):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="dict")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        dict_attr = {"a": np.nan, "b": 2, "c": "hi"}

        dict_unfrozen = test_fun(a=10, b=11, the_arg=dict_attr)

        assert dict_attr == dict_unfrozen


    def test5_index_series(self):

        @freeze_unhashable(freeze_by="index", freeze_index=0)
        def test_fun(the_arg, a, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        df = pd.DataFrame({"a": [1,2,3,np.nan], "b": ["x", "y", "z", np.nan]})

        s = df["a"]

        s_unfrozen = test_fun(s, 10, 11)

        pd.testing.assert_series_equal(s, s_unfrozen)


    def test6_index_series_kwargs(self):

        @freeze_unhashable(freeze_by="index", freeze_index=0)
        def test_fun(the_arg, a, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        df = pd.DataFrame({"a": [1,2,3,np.nan], "b": ["x", "y", "z", np.nan]})

        s = df["a"]

        s_unfrozen = test_fun(the_arg=s, a=10, b=11)

        pd.testing.assert_series_equal(s, s_unfrozen)


    def test7_index_series_kwargs_noattrib(self):

        @freeze_unhashable(freeze_by="index", freeze_index=0)
        def test_fun(the_arg, a, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        s_unfrozen = test_fun(the_arg=[], a=10, b=11)

        assert s_unfrozen == []


    def test8_index_series_diffindex(self):

        @freeze_unhashable(freeze_by="index", freeze_index=1)
        def test_fun(a, the_arg, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="series")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        df = pd.DataFrame({"a": [1,2,3,np.nan], "b": ["x", "y", "z", np.nan]})

        s = df["a"]

        s_unfrozen = test_fun(10, s, b=11)

        pd.testing.assert_series_equal(s, s_unfrozen)


    def test9_index_dict(self):

        @freeze_unhashable(freeze_by="index", freeze_index=0)
        def test_fun(the_arg, a, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="dict")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        dict_attr = {"a": np.nan, "b": 2, "c": "hi"}

        dict_unfrozen = test_fun(dict_attr, 10, 11)

        assert dict_attr == dict_unfrozen


    def test10_index_dict_noattrib(self):

        @freeze_unhashable(freeze_by="index", freeze_index=0)
        def test_fun(the_arg, a, b, c=12):

            the_arg = unfreeze_unhashable(the_arg, frozen_type="dict")

            if a == 10 and b == 11 and c == 12:

                return the_arg

            else:

                return None

        dict_unfrozen = test_fun([], 10, 11)

        assert dict_unfrozen == []


