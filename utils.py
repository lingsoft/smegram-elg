import subprocess
import json

from elg.model import TextsResponseObject
from elg.model.base import Annotation


def runcmd(command):
    ret = subprocess.run(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding="utf-8",
                         timeout=30)
    if ret.returncode == 0:
        print("success:")
    else:
        print("error:")
    return ret


def gmr_func_elg(text, pipe):
    """
    :param text: str
    :return
    """
    res_str = runcmd("echo \"%s\" \
                    | divvun-checker -s se/pipespec.xml -n %s" %
                     (text, pipe)).stdout
    # print('original res_str', res_str)
    if not res_str:
        raise Exception('Internal error')

    res = json.loads(res_str)
    # print('res from native util', res)
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