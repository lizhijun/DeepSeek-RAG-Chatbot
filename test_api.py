import unittest
import json
from api import app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_api_status(self):
        """测试API基本状态"""
        # 测试文档列表接口
        response = self.app.get('/api/documents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('documents', data)

if __name__ == '__main__':
    unittest.main() 