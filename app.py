from elg import FlaskService
from elg.model import Failure
from elg.model import TextRequest
from elg.model import AnnotationsResponse
from elg.model.base import Annotation
from elg.model.base import StandardMessages
from elg.model.base import StatusMessage

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
            annotations = {}
            for e in errors:
                features={
                        "explanation": e.msg,
                        "suggestion": list(e.rep)}
                annotation = {
                        "start": e.beg,
                        "end": e.end,
                        "features": features}
                annotations.setdefault(e.err, []).append(annotation)
            resp = AnnotationsResponse(annotations=annotations)
            warning = None
            if any(ord(ch) > 0xffff for ch in text):
                warning = StatusMessage(
                    code="lingsoft.request.character.unsupported",
                    params=[],
                    text="Standoffs may fail because text contains characters from supplementary planes")
            if warning:
                resp.warnings = [warning]
            return resp
        except Exception as err:
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(err)])
            return Failure(errors=[error])


flask_service = SamiChecker("sami-checker")
app = flask_service.app
