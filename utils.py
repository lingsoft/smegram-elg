import subprocess
import json

import logging

from elg.model import TextsResponseObject
from elg.model.base import Annotation

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
        logging.error("Something wrong!")
    return ret


def gmr_func_elg(text, pipe):
    """
    :param text: str
    :return
    """

    res_str = runcmd("echo \"%s\" \
                    | divvun-checker -s se/pipespec.xml -n %s" %
                     (text, pipe)).stdout

    if not res_str:
        raise Exception('Internal error')

    res = json.loads(res_str)
    content = res['text']
    errs = res['errs']
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
    return TextsResponseObject(content=content, annotations={"errs": annos})
