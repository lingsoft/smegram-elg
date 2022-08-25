from elg import FlaskService
from elg.model import Failure
from elg.model import TextRequest
from elg.model.base import StandardMessages

import utils


class SamiChecker(FlaskService):

    MAX_CHAR = 3750

    def process_text(self, request: TextRequest):

        text = request.content
        if len(text) > self.MAX_CHAR:
            error = StandardMessages.generate_elg_request_too_large()
            return Failure(errors=[error])

        try:
            pipe = "smegram"
            res = utils.gmr_func_elg(text, pipe)
            return res
        except Exception as err:
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(err)])
            return Failure(errors=[error])


flask_service = SamiChecker("sami-checker")
app = flask_service.app
