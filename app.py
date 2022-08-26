from elg import FlaskService
from elg.model import Failure
from elg.model import TextRequest
from elg.model import AnnotationsResponse
from elg.model.base import Annotation
from elg.model.base import StandardMessages
# from elg.model.base import StatusMessage

import libdivvun


spec = libdivvun.ArCheckerSpec("se.zcheck")
smegram = spec.getChecker("smegramrelease", True)


class SamiChecker(FlaskService):

    MAX_CHAR = 3750

    def process_text(self, request: TextRequest):

        text = request.content
        if len(text) > self.MAX_CHAR:
            error = StandardMessages.generate_elg_request_too_large()
            return Failure(errors=[error])
        try:
            errors = libdivvun.proc_errs_bytes(smegram, text)
            annos = []
            for e in errors:
                annos.append(
                    Annotation(start=e.beg,
                            end=e.end,
                            features={
                                "original": e.form,
                                "type": e.err,
                                "explanation": e.msg,
                                "suggestion": list(e.rep)
                            }))
            return AnnotationsResponse(annotations={"errs": annos})
        except Exception as err:
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(err)])
            return Failure(errors=[error])


flask_service = SamiChecker("sami-checker")
app = flask_service.app
