from kgextension.utilities_helper import is_valid_url, url_exists
import pytest
import numpy as np

class TestIsValidURL:

    def test1(self):
        
        assert is_valid_url("wikidata.org/wiki/Q985") == False

    def test2(self):
        
        assert is_valid_url("www.google.de") == False
        
    def test3(self):
        
        assert is_valid_url("https://www.münchen.de") == True
        
    def test4(self):
        
        assert is_valid_url("http://www.münchen.de") == True
        
    def test5(self):
        
        assert is_valid_url("https://levelup.gitconnected.com/how-to-build-a-diy-web-scraper-in-any-language-1104ac0713cd") == True
        
    def test6(self):
        
        assert is_valid_url("https://www.wikidata.org/wiki/Q985") == True
                
    def test7(self):
        
        assert is_valid_url("https://www.wikidata.org/wiki test/Q985") == False

    def test8(self):
        
        assert is_valid_url("") == False


class TestUrlExists:

    def test1(self):
        
        assert url_exists("https://www.google.com") == True

    def test2(self):
        
        assert url_exists("https://www.youtube.com/") == True
        
    def test3(self):
        
        assert url_exists("https://facebook.com/") == True
        
    def test4(self):
        
        assert url_exists("http://www.baidu.com") == True
        
    def test5(self):
        
        assert url_exists("https://www.randomdomainthatdoesntexist.com") == False
        
    def test6(self):
        
        assert url_exists("") == False
                
    def test7(self):
        
        assert url_exists("https://www.wikidata.org/wiki test/Q985") == False

    def test8(self):
        
        assert url_exists("https://www.wikidata.org/wikiabs") == False

    def test9(self):
        
        assert url_exists("https://www.wikidata.org/wiki/Q59645613541") == False
        
    def test10(self):
        
        assert url_exists(np.nan) == False