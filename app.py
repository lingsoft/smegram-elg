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
            line_begin = 0
            annotations = {}
            for line in text.splitlines():
                errors = libdivvun.proc_errs_bytes(smegram, line)
                for e in errors:
                    features={
                            "explanation": e.msg,
                            "description": e.dsc,
                            "suggestion": list(e.rep)}
                    annotation = {
                            "start": line_begin + e.beg,
                            "end": line_begin + e.end,
                            "features": features}
                    annotations.setdefault(e.err, []).append(annotation)
                line_begin += len(line) + 1
            resp = AnnotationsResponse(annotations=annotations)
            warning = None
            if any(ord(ch) > 0xffff for ch in text):
                warning = StatusMessage(
                    code="lingsoft.request.character.unsupported",
                    params=[],
                    text="Characters from supplementary planes may mess offsets")
            if warning:
                resp.warnings = [warning]
            return resp
        except Exception as err:
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(err)])
            return Failure(errors=[error])


flask_service = SamiChecker("sami-checker")
app = flask_service.app
