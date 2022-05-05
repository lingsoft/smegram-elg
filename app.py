from distutils import errors
import utils
from elg import FlaskService
from elg.model import Failure
from elg.model import TextsResponse, TextRequest
from elg.model.base import StandardMessages


class SamiChecker(FlaskService):

    available_pipes = [
        'smegramrelease', 'smegram', 'smespell', 'smegram-nospell'
    ]

    def check_params(self, request):
        params = request.params
        if not params:
            return False
        if 'pipe' not in params:
            return False
        pipe = params['pipe']
        if pipe not in self.available_pipes:
            return False
        return pipe

    def process_text(self, request: TextRequest):

        text = request.content
        pipe = self.check_params(request)
        if not pipe:
            # missing parameter
            detail = {
                'params':
                f'no given params or invalid params, support pipes are: {self.available_pipes}'
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
