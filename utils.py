import subprocess
import json
import logging
# import difflib

from elg.model import AnnotationsResponse
from elg.model.base import Annotation
from elg.model.base import StatusMessage

log_format = '%(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format)


def runcmd(command):
    ret = subprocess.run(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding="utf-8",
                         timeout=30)
    if ret.returncode == 0:
        logging.info("success in calling the se CLI")
    else:
        logging.error("Subprocess returncode %s", ret.returncode)
    return ret


def gmr_func_elg(text, pipe):

    res_str = runcmd("echo \"%s\" \
                    | divvun-checker -s se/pipespec.xml -n %s" %
                     (text, pipe)).stdout

    if not res_str:
        raise Exception("Subprocess returned nothing")

    res = json.loads(res_str)
    content = res['text']
    warning = None
    if text != content:
        # diffs = [c for c in difflib.ndiff(text, content) if c[0] != ' ']
        logging.warning("Origin: %s, returned: %s", len(text), len(content))
        # logging.warning("Differences: %s", diffs)
        warning = StatusMessage(
            code="lingsoft.texts.mismatch",
            params=[],
            text="Original text and return content are difference")

    errs = res["errs"]
    annos = []
    for e in errs:
        annos.append(
            Annotation(start=e[1],
                       end=e[2],
                       features={
                           "original": e[0],
                           "type": e[3],
                           "explanation": e[4],
                           "suggestion": e[5]
                       }))
    resp = AnnotationsResponse(annotations={"errs": annos})
    if warning:
        resp.warnings = [warning]
    return resp
