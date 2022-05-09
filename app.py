from distutils import errors
import utils
from elg import FlaskService
from elg.model import Failure
from elg.model import TextsResponse, TextRequest
from elg.model.base import StandardMessages


class SamiChecker(FlaskService):

    available_pipes = ['smegramrelease', 'smegram']
    max_char = 4095
    min_char = 2

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
        if len(text) < self.min_char:
            tooShortMessage = StandardMessages.generate_elg_request_invalid(
                detail={'text': 'lower limit is 2 characters in length'})
            return False, Failure(errors=[tooShortMessage])
        elif len(text) > self.max_char:
            tooLargeMessage = StandardMessages.generate_elg_request_too_large()
            return False, Failure(errors=[tooLargeMessage])
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
        return TextsResponse(texts=[res])


flask_service = SamiChecker("sami-grm-checker")
app = flask_service.app
