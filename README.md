# ELG API for Sami grammar checker

This git repository contains
[ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html)
Flask based REST API for the Sami grammar checker.

[lang-sme](https://github.com/giellalt/lang-sme) contains finite state
source files for the North Sami language, for building morphological
analyzers, proofing tools, and dictionaries. It is published under GPL-3.0 License.
Original authors are from [GiellaLT](https://giellalt.uit.no).
More info can be found in this [paper](https://ep.liu.se/ecp/168/008/ecp19168008.pdf)

This ELG API was developed in EU's CEF project:
[Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry)

## Local development

### Language files

#### Build from source

The grammar tool can be built from source as described in the `Dockerfile.build`.
To run it, at least 8GB memory is required.

```
docker build -f Dockerfile.build -t lang-sme .
```

Then run the container and copy the zcheck file from the container
```
docker run --name -it -d sme-src lang-sme
docker cp lang-sme:/home/lang-sme/tools/grammarcheckers/se.zcheck
```

#### Download pre-built files

TODO

#### Command-line tool

The tool is located inside the directory `se` and instant test can be done likes
```
cd se
echo “boazodoallo guovlu” | divvun-checker -s pipespec.xml -n smegram
```

The result should look like

```json
{
  'errs': 
    [
        [
          'boazodoallo guovlu',
          0,
          18,
          'Msyn-compound',
          '"boazodoallo guovlu" orru leamen goallossátni',
          ['boazodoalloguovlu'],
          'Goallosteapmi'
        ]
    ],
   'text': 'boazodoallo guovlu'
}
```

The array-of-arrays errs has one array per error.
Within each error-array, beg/end are offsets in text, typ is the (internal)
error type, exp is the human-readable explanation, and each rep is a possible
suggestion for replacement of the text between beg/end in text.

The index beg is inclusive, end exclusive, and both indices are based on a
UTF-16 encoding (which is what JavaScript uses, so e.g. the emoji “norway”
will increase the index of the following errors by 4).

### Virtual environment

Setup virtualenv, dependencies
```
python3 -m venv lang-sme-elg-venv
source lang-sme-elg-venv/bin/activate
python3 -m pip install -r requirements.txt
```

Run the development mode flask app
```
FLASK_ENV=development flask run --host 0.0.0.0 --port 8000
```

### Tests

```
python3 -m unittest  -v
```

## Building the docker image

```
docker build -t smegram-elg .
```

Or pull directly ready-made image `docker pull lingsoft/smegram-elg:tagname`.

## Deploying the service

```
docker run -p <port>:8000 --init smegram-elg
```

## Example call

```
curl -H 'Content-Type: application/json' -d @sample.json http://localhost:8000/process
```

### sample.json

```json
{
    "type": "text",
    "content": "Oktiibuot 13 Norgag doaktára leat leamaš mielde dáin iskkadan bargguin ."
}
```

### Response

```json
{
  "response": {
    "type": "annotations",
    "annotations": {
      "typo": [
        {
          "start": 13,
          "end": 19,
          "features": {
            "explanation": "Čállinmeattáhus",
            "suggestion": [
              "Borga",
              "Čorgat",
              "Borgan",
              "Borgat",
              "Norga",
              "Jorgal",
              "Jorgas",
              "Čorga",
              "Čorgago",
              "Borgago"
            ]
          }
        }
      ],
      "space-before-punct-mark": [
        {
          "start": 53,
          "end": 72,
          "features": {
            "explanation": "Sátnegaskameattáhus",
            "suggestion": [
              "iskkadan bargguin."
            ]
          }
        }
      ]
    }
  }
}
```
