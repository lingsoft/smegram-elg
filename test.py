import json
import unittest
import os
import requests


class TestResponse(unittest.TestCase):
    base_url = 'http://localhost:8000/process'

    base_text = ["boazodoallo guovlu"]
    MAX_CHAR = 4095
    CONTROL_CHARS = ['\r', '\n', '\t', '\u2028', '\u2029']

    pipes = ["smegramrelease", "smegram"]
    params = {"pipe": pipes[1]}
    payload = json.dumps({
        "type": "text",
        "params": params,
        "content": base_text[0]
    })

    headers = {'Content-Type': 'application/json'}

    def test_api_response_status_code(self):
        """Should return status code 200
        """

        status_code = requests.post(self.base_url,
                                    headers=self.headers,
                                    data=self.payload).status_code
        self.assertEqual(status_code, 200)

    def test_valid_api_response(self):
        """Return response should not be empty
        """

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=self.payload).json()['response']
        self.assertNotEqual(response, None)

    def test_api_response_type(self):
        """Should return ELG annotation response type
        """

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=self.payload).json()['response']
        self.assertEqual(response.get('type'), 'texts')

    def test_api_response_when_no_given_param(self):
        """API should work with default pipeline
        when there is no pipeline in params
        """

        payload_dict = {"type": "text", "content": self.base_text[0]}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()['response']['texts'][0]

        self.assertIn('errs', response['annotations'])

        for _ in ['start', 'end', 'features']:
            self.assertIn(_, response['annotations']['errs'][0])

        for prop in ['original', 'type', 'explanation', 'suggestion']:

            self.assertIn(prop, response['annotations']['errs'][0]['features'])

    def test_api_response_content(self):
        """Should return correct content with two
        different grammar check pipelines
        """

        for pipe in self.pipes:
            print(f'testing with pipe: {pipe}')
            params = {"pipe": pipe}
            payload_dict = {
                "type": "text",
                "params": params,
                "content": 'Prošeatadoarjagat'
            }
            payload = json.dumps(payload_dict)
            response = requests.post(
                self.base_url, headers=self.headers,
                data=payload).json()['response']['texts'][0]

            self.assertIn('errs', response['annotations'])

            for _ in ['start', 'end', 'features']:
                self.assertIn(_, response['annotations']['errs'][0])

            for prop in ['original', 'type', 'explanation', 'suggestion']:

                self.assertIn(prop,
                              response['annotations']['errs'][0]['features'])

    def test_api_response_with_limit_large_req(self):
        """Should return correct response with
        the maximum allow content request
        """

        large_text = '. '.join(self.base_text * 230)
        assert len(large_text) > self.MAX_CHAR, 'text is not large enough'

        payload_dict = {
            "type": "text",
            "params": self.params,
            "content": large_text[:self.MAX_CHAR]
        }
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()['response']['texts'][0]

        self.assertIn('errs', response['annotations'])

        for _ in ['start', 'end', 'features']:
            self.assertIn(_, response['annotations']['errs'][0])

        for prop in ['original', 'type', 'explanation', 'suggestion']:

            self.assertIn(prop, response['annotations']['errs'][0]['features'])

    def test_api_response_with_too_large_req(self):
        """Should return Failure with too large request which
        exceeds 15000-char length
        """

        large_text = '. '.join(self.base_text * 230)
        assert len(large_text) > 4095, 'text is not large enough'

        payload_dict = {
            "type": "text",
            "params": self.params,
            "content": large_text
        }
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.too.large')

    def test_api_response_with_empty_request(self):
        """Should return invalid request prompt
        """

        payload_dict = {"type": "text", "params": self.params, "content": ""}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.invalid')

    def test_api_response_with_too_short_request(self):
        """Should return invalid request prompt
        """

        payload_dict = {"type": "text", "params": self.params, "content": "a"}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.invalid')

    def test_api_response_when_content_has_ctrl_char(self):
        """API should return failture when there is
        control characters in the content
        """

        for chr in self.CONTROL_CHARS:

            content = self.base_text[0] + chr
            payload_dict = {"type": "text", "content": content}
            payload = json.dumps(payload_dict)
            response = requests.post(self.base_url,
                                     headers=self.headers,
                                     data=payload).json()

            self.assertIn('failure', response)
            self.assertEqual(response['failure']['errors'][0]['code'],
                             'elg.request.invalid')
            self.assertEqual(
                response['failure']['errors'][0]['detail']['text'],
                'There is control character in the content')

    def test_api_response_when_content_has_extra_white_space(self):
        """API should return failture when there is
        extra white spaces in the content
        """

        content = self.base_text[0][:10] + '  ' + self.base_text[0][10:]
        payload_dict = {"type": "text", "content": content}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.invalid')
        self.assertEqual(response['failure']['errors'][0]['detail']['text'],
                         'There is too many white space in the content')


if __name__ == '__main__':
    unittest.main()
