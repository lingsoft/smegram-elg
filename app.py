import utils
from elg import FlaskService
from elg.model import Failure
from elg.model import TextsResponse, TextRequest
from elg.model.base import StandardMessages

import re


class SamiChecker(FlaskService):

    available_pipes = ['smegramrelease', 'smegram']
    MAX_CHAR = 4095
    MIN_CHAR = 2
    CONTROL_CHARS = ['\r', '\n', '\t', '\u2028', '\u2029']

    def check_params(self, request):
        params = request.params
        default_pipe = self.available_pipes[1]
        if not params:
            return default_pipe
        if 'pipe' not in params:
            return default_pipe
        pipe = params['pipe']
        if pipe not in self.available_pipes:
            return False
        return pipe

    def check_text(self, text):
        text = text.strip()
        if len(text) < self.MIN_CHAR:
            tooShortMessage = StandardMessages.generate_elg_request_invalid(
                detail={'text': 'lower limit is 2 characters in length'})
            return False, Failure(errors=[tooShortMessage])
        elif len(text) > self.MAX_CHAR:
            tooLargeMessage = StandardMessages.generate_elg_request_too_large()
            return False, Failure(errors=[tooLargeMessage])
        elif any(c in self.CONTROL_CHARS for c in text):
            inputHasControlCharMessage = StandardMessages.generate_elg_request_invalid(
                detail={'text': 'There is control character in the content'})
            return False, Failure(errors=[inputHasControlCharMessage])
        elif re.search(r'(\s\s+)', text):
            inputHasExtraWhiteSpaceMessage = StandardMessages.generate_elg_request_invalid(
                detail={
                    'text': 'There is too many white space in the content'
                })
            return False, Failure(errors=[inputHasExtraWhiteSpaceMessage])
        else:
            return True, text

    def process_text(self, request: TextRequest):

        text = request.content
        text_ok, text_check_res = self.check_text(text)
        if not text_ok:
            return text_check_res

        pipe = self.check_params(request)
        if not pipe:
            # missing parameter
            detail = {
                'params':
                f'invalid params, support pipes are: {self.available_pipes}'
            }
            missingRequestMsg = StandardMessages.generate_elg_request_missing(
                detail=detail)
            return Failure(errors=[missingRequestMsg])

        try:
            res = utils.gmr_func_elg(text, pipe)
        except Exception as err:
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(err)])
            return Failure(errors=[error])
        return res


flask_service = SamiChecker("sami-grm-checker")
app = flask_service.app
