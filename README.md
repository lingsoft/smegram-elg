# ELG API for Northern Sami grammar checker

This git repository contains
[ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html)
Flask based REST API for the Sami grammar checker.

## Authors

### Original authors

[lang-sme](https://github.com/giellalt/lang-sme) GPL-3.0 License.
Finite state and Constraint Grammar based analysers and proofing tools,
and language resources for the Northern Sami language.
Original authors are from [GiellaLT](https://giellalt.uit.no).

More info can be found from Wiechetek et al. (2019).
[Many shades of grammar checking – Launching a Constraint Grammar tool for North Sámi](https://ep.liu.se/en/conference-article.aspx?series=ecp&issue=168&Article_No=8)

[libdivvun](https://github.com/divvun/libdivvun)
is a library for handling Finite-State Morphology and Constraint Grammar
based NLP tools in GiellaLT. The tools are used for tokenisation,
normalisation, grammar-checking and correction, and other NLP tasks.
GPL-3.0 License.

The architecture of systems using libdivvun is described in
Wiechetek, L., Moshagen, S., & Unhammer, K. B. (2019, February).
[Seeing more than whitespace—Tokenisation and disambiguation in a North Sámi grammar checker](https://aclanthology.org/W19-6007.pdf).
In Proceedings of the 3rd Workshop on the Use of Computational Methods in
the Study of Endangered Languages Volume 1 (Papers) (pp. 46-55).

### ELG API

This ELG API was developed in EU's CEF project:
[Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry)

## Development

### Language files

#### Build from source

The grammar tool can be built from source as described in the `Dockerfile.build`.
To run it, at least 8GB memory is required.

```
docker build -f Dockerfile.build -t lang-sme .
```

Then run the container and copy the zcheck file from the container
```
docker run -it -d lang-sme bash
docker cp <container_name>:/home/lang-sme/tools/grammarcheckers/se.zcheck
```

#### Download speller and grammar archives

Easiest way is to get https://github.com/divvun/divvun-ci-config
and download the archives by following these
[instructions](https://github.com/divvun/divvun-api/tree/main/deployment).

(Or wget giella-sme-speller deb package and dpkg-deb -xv)

### Virtual environment

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Run the development mode flask app
```
FLASK_ENV=development flask run --host 0.0.0.0 --port 8000
```

### Tests

```
python3 -m unittest -v
```

## Usage

### Building the docker image

```
docker build -t smegram-elg .
```

Or pull directly ready-made image `docker pull lingsoft/gramdivvun:tagname`.

### Deploying the service

```
docker run -p <port>:8000 --init smegram-elg
```

### Example call

```
curl -H 'Content-Type: application/json' -d @sample.json http://localhost:8000/process
```

#### sample.json

```json
{
    "type": "text",
    "content": "Oktiibuot 13 Norgag doaktára leat leamaš mielde dáin iskkadan bargguin ."
}
```

#### Response

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
            "description": "Ii leat sátnelisttus",
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
            "description": "Lea gaska \".\" ovddas",
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

### Local ELG GUI

Use ELG-compatible service from GUI locally

```
cd elg_local && docker-compose up
```

The GUI is accessible on `http://localhost:5080`. See more
[instructions](https://european-language-grid.readthedocs.io/en/stable/all/A1_PythonSDK/DeployServicesLocally.html#deploy-elg-compatible-service-from-its-docker-image).
