import json
from unittest import TestCase
from model import (connect_to_db,db,User,Movie,Source,MovieSource,Genre,MovieGenre,MovieWatched)
from server import app
import server

class FlaskTestBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        #Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page when user not logged in"""

        result = self.client.get("/")
        self.assertEqual(result.status_code,200)
        self.assertIn('<a href="/browse">Browse</a>', result.data)  


class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        connect_to_db(app)
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def test_home_page(self):
        """Test homepage when user is logged in."""

        result = self.client.get("/",follow_redirects=True)
        self.assertIn('<a href="/watchlist">My Watch List</a>', result.data)
        self.assertNotIn('<a href="/browse">Browse</a>', result.data)
        self.assertIn('<a href="/signout">Sign Out', result.data)







if __name__ == "__main__":
    import unittest

    unittest.main()