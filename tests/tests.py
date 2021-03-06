import os
import hrf
import unittest
import json

directory = os.path.dirname(__file__)

class HrfTestCase(unittest.TestCase):
    def setUp(self):
        self.app = hrf.app.test_client()

    def test_json1_title(self):
        json_input = file(os.path.join(directory, '1.json'), 'r').read()
        post = json.loads(self.app.post('/title', data=json_input).data)
        assert post['results'][0] == 'buildsys.build.state.change'

    def test_json1_all(self):
        json_input = file(os.path.join(directory, '1.json'), 'r').read()
        post = json.loads(self.app.post('/all', data=json_input).data)
        assert post['results'][0]['title'] == 'buildsys.build.state.change'
        assert post['results'][0]['repr'] == 'buildsys.build.state.change -- uthash-1.9.8-3.el6 started building http://koji.fedoraproject.org/koji/buildinfo?buildID=430456'
        assert post['results'][0]['icon'] == 'http://fedoraproject.org/w/uploads/2/20/Artwork_DesignService_koji-icon-48.png'

    def test_json2_all(self):
        json_input = file(os.path.join(directory, '2.json'), 'r').read()
        post = json.loads(self.app.post('/all', data=json_input).data)

        assert post['results'][0]['title'] == 'bodhi.update.request.testing'
        assert post['results'][0]['repr'] == 'bodhi.update.request.testing -- cicku submitted uthash-1.9.8-3.fc18 to testing https://admin.fedoraproject.org/updates/uthash-1.9.8-3.fc18'
        assert post['results'][0]['icon'] == 'https://admin.fedoraproject.org/updates/static/images/bodhi-icon-48.png'

        assert post['results'][1]['title'] == 'buildsys.build.state.change'
        assert post['results'][1]['repr'] == 'buildsys.build.state.change -- uthash-1.9.8-3.el6 started building http://koji.fedoraproject.org/koji/buildinfo?buildID=430456'
        assert post['results'][1]['icon'] == 'http://fedoraproject.org/w/uploads/2/20/Artwork_DesignService_koji-icon-48.png'

    def test_json1_timezone1(self):
        json_input = file(os.path.join(directory, '1.json'), 'r').read()
        post1 = json.loads(self.app.post('/timestamp?timezone=US/Eastern', data=json_input).data)
        post2 = json.loads(self.app.post('/timestamp', data=json_input).data)
        assert post1['results'][0]['iso'] != post2['results'][0]['iso']
        assert post1['results'][0]['time'] != post2['results'][0]['time']

    def test_json1_timezone_error(self):
        json_input = file(os.path.join(directory, '1.json'), 'r').read()
        post = json.loads(self.app.post('/timestamp?timezone=invalid/invalid', data=json_input).data)
        assert post['error'] == "Invalid timezone parameter."

    def test_json1_method_error(self):
        json_input = file(os.path.join(directory, '1.json'), 'r').read()
        post = json.loads(self.app.post('/derpderp', data=json_input).data)
        assert post['error'] == "That method was invalid."

if __name__ == '__main__':
    unittest.main()
