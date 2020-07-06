import requests
import unittest

# 查询发布会接口
class GetEventList(unittest.TestCase):

    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/get_event_list"

    # 发布回id为空的结果
    def test_get_event_null(self):
        '''发布会id为空'''
        r = requests.get(self.url,params={'eid':''})
        result = r.json()
        print(result)
        self.assertEqual(result['status'], 10021)
        self.assertEqual(result['message'] , "parameter error")

    # 发布会id为1的查询结果
    def test_get_event_success(self):
        r = requests.get(self.url, params={'eid':'1'})
        result = r.json()
        print(result)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], "success")
        self.assertEqual(result['data']['name'], "小米5发布会")
        self.assertEqual(result['data']['limit'], 1000)
        self.assertEqual(result['data']['address'], "北京")
        self.assertEqual(result['data']['start_time'], "2019-12-30T20:00:00")


if __name__ == '__main__':
    unittest.main()
