import unittest
import requests
import json


endpoint = 'http://localhost:8000/process'


def create_payload(text):
    return {"type": "text", "content": text}


def call_api(payload):
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps(payload)
    return requests.post(
            endpoint, headers=headers, data=payload).json()


class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Wiechetek et al. (2019). Many shades of grammar checking
        # https://ep.liu.se/ecp/168/008/ecp19168008.pdf
        self.text = "Oktiibuot 13 Norgag doaktára leat leamaš mielde dáin iskkadan bargguin ."
        self.compound_text = "boazodoallo guovlu"

    def test_api_response_type(self):
        payload = create_payload(self.text)
        response = call_api(payload)
        self.assertEqual(response["response"]["type"], "annotations")

    def test_api_response_content(self):
        payload = create_payload(self.compound_text)
        response = call_api(payload)
        self.assertIn("msyn-compound", response["response"]["annotations"])

    def test_api_response_with_empty_text(self):
        payload = create_payload("")
        response = call_api(payload)
        self.assertIn("annotations", response["response"])

    def test_api_response_with_newline_text(self):
        text = self.compound_text + "\n" + self.compound_text + "\n" + self.compound_text
        payload = create_payload(text)
        response = call_api(payload)
        print(text)
        print(response)
        third_line = response["response"]["annotations"]["msyn-compound"][2]
        self.assertEqual(third_line["start"], 38)

    def test_api_response_with_too_long_text(self):
        n_sents = int(3750 / (len(self.text) + 1)) + 1
        long_text = (" ".join([self.text] * n_sents))
        payload = create_payload(long_text)
        response = call_api(payload)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                         "elg.request.too.large")

    def test_api_response_with_long_token(self):
        long_token = "å" * 1000
        payload = create_payload(long_token)
        response = call_api(payload)
        self.assertIn("typo", response["response"]["annotations"])

    def test_api_response_with_unsupported_characters(self):
        spec_text = "\N{grinning face}" + self.compound_text
        payload = create_payload(spec_text)
        response = call_api(payload)
        self.assertGreater(len(response["response"]["warnings"]), 0)

    def test_api_response_with_wrong_language(self):
        wrong_lang = "使用人口について正確な統計はないが、日本国内の人口、"
        payload = create_payload(wrong_lang)
        response = call_api(payload)
        self.assertIn("annotations", response["response"])


if __name__ == '__main__':
    unittest.main()
