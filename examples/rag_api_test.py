import os
import unittest
import requests
from dotenv import load_dotenv

load_dotenv()

class TestRAGAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "f79552ee-8d92-48a1-afdc-6b58c09a959e"
        self.base_url = os.getenv('RAG_API_URL')
        self.headers = {
            'Authorization': f'ApiKey {self.api_key}',
            'Content-Type': 'application/json'
        }

    def test_api_connectivity(self):
        """Test basic API connectivity"""
        url = f'{self.base_url}/query'
        try:
            response = requests.post(url, headers=self.headers, json={'query': 'test'})
            response.raise_for_status()
            self.assertTrue(response.ok)
            print(f"API connectivity successful. Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"API connectivity failed: {e}")
            self.fail(f"API connectivity failed: {e}")

    def test_valid_api_key(self):
        """Test if the API key is valid"""
        url = f'{self.base_url}/query'
        try:
            response = requests.post(url, headers=self.headers, json={'query': 'test'})
            response.raise_for_status()
            self.assertTrue(response.ok)
            print(f"API key is valid. Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"API key validation failed: {e}")
            self.fail(f"API key validation failed: {e}")

if __name__ == '__main__':
    unittest.main()