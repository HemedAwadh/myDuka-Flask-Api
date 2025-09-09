import unittest
from app.main import app
import json

class FlaskAPITest(unittest.TestCase):
    token = ""
    headers = {}

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 

    def test_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"Flask-Api": "1.0"})

    def test_login(self):
        response = self.app.post('/login',data = json.dumps({"email": "awadh@gmail.com","password":"123"}),
                                 content_type= 'application/json')
        
        self.assertEqual(response.status_code, 200)
        #store token in global variable
        self.token = response.get_json()["token"]
        self.headers = {"Authorization" : "Bearer " + self.token , "Content-Type" : "application/json" }
        print(self.token)

    def test_products(self):
        ## call test_login() so that headers is given the token value
        self.test_login()
        response = self.app.get('/api/products', headers = self.headers)
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_add_products(self):
        ## call test_login() so that headers is given the token value
        self.test_login()
        response = self.app.post("/api/products", data = json.dumps({"name": "Bread","buying_price":10 , "selling_price":45}),
                                 headers = self.headers,content_type= 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"name": "Bread","buying_price":10 , "selling_price":45})


        print(response.get_json())
    


if __name__ =="__main__":
        unittest.main()        