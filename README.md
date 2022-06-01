# ELG API for Sami grammar speller and checker

This git repository contains [ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html) Flask based REST API for the Sami speller and checker.

[lang-sme](https://github.com/giellalt/lang-sme) contains finite state source files for the North Sami language, for building morphological analyzers, proofing tools, and dictionaries. It is published under GPL-3.0 License.
Original authors are from [GiellaLT](https://giellalt.uit.no). More info can be found in this [paper](https://ep.liu.se/ecp/168/008/ecp19168008.pdf)

This ELG API was developed in EU's CEF project: [Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry)

## Local development

### Building the tool from source

The grammar tool can be built from source as described in the `Dockerfile.build`. To run it, at least 8GB memory is required.
```
docker build -f Dockerfile.build -t lang-sme .
```

Then run the container and copy the zcheck file from the container
```
docker run --name -it -d sme-src lang-sme 
docker cp lang-sme:/home/lang-sme/tools/grammarcheckers/se.zcheck
```

### Use the pre-built `se.zip` file

The grammar tool is packed in the se.zip file, extracting the file
```
unzip se.zip && rm se.zip
```

The tool is located inside the directory `se` and instant test can be done likes
```
cd se
echo “boazodoallo guovlu” | divvun-checker -s pipespec.xml -n smegram
```

The result should look like
```
{
  'errs': 
    [
        [
          'boazodoallo guovlu',
          0, //beg offset
          18, // end offset
          'Msyn-compound', // internal error type
          '"boazodoallo guovlu" orru leamen goallossátni', // human-readable explanation
          ['boazodoalloguovlu'], // possible suggestion
          'Goallosteapmi'
        ]
    ],
   'text': 'boazodoallo guovlu'
}
```
The array-of-arrays errs has one array per error. Within each error-array, beg/end are offsets in text, typ is the (internal) error type, exp is the human-readable explanation, and each rep is a possible suggestion for replacement of the text between beg/end in text.

The index beg is inclusive, end exclusive, and both indices are based on a UTF-16 encoding (which is what JavaScript uses, so e.g. the emoji “norway” will increase the index of the following errors by 4).


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

## Running tests

```
python3 -m unittest  -v
```

## Building the docker image

```
docker build -t lang-sme-elg .
```

Or pull directly ready-made image `docker pull lingsoft/lang-sme:tagname`.

## Deploying the service

```
docker run -d -p <port>:8000 --init --memory="4g" --restart always lang-sme-elg
```

## REST API

### Call pattern

#### URL

```
http://<host>:<port>/process
```

Replace `<host>` and `<port>` with the hostname and port where the 
service is running.

#### HEADERS

```
Content-type : application/json
```

#### BODY

For text request
```
{
  "type":"text",
  "params":{"pipe":str},
  "content": text to be checked
}
```

Property `params` (optional) contains {"pipe": "valid_pipe"} where `valid_pipe` (default is `smegram`) is one of two supported pre-defined pipelines: 
- smegramrelease : Spelling and grammar error
- smegram : Spelling and grammar error with a after-speller-disambiguator

The value of property content should be in range [2:4095] characters in length. The number 4095 was selected based on empirical experiments on the maximum sentence length the pipeline can handle. In addition, the content should not contain any extra whitespaces or control characters or newlines since this can cause unexpected offset mismatches. In that case, ELG Failure response will be returned.


#### RESPONSE

Text response
```
{
  "response":{
    "type":"texts",
    "texts":[
              {
                "content": "string of the requested text",
                "annotations": {
                  "errs": [
                      {
                        "original": "string of original words",
                        "start": start offset,
                        "end": end offset,
                        "type": error type,
                        "explanation": "string of explanation",
                        "suggestions": List[string of suggestion] 
                      },
                  ] 
                }
                     
              },
          ]
  }
}
```

### Response structure

The array-of-arrays `errs` has one array per error. Within each error array:
- `original` is the original text that is detected
- `start`/`end` are offsets in text
- `type` is the (internal) error type
- `explanation` is the human-readable explanation
- `suggestion` is a list of possible suggestions for replacement of the `original` text in the content.

### Example call

```
 curl -d '{"type":"text", "params": {"pipe": "smegram"}, "content": "boazodoallo guovlu"}' -H "Content-Type: application/json" -X POST http://localhost:8000/process
```

### Response should be

```
{
  "response": {
    "type": "annotations",
    "annotations": {
      "errs": [
        {
          "start": 0,
          "end": 18,
          "features": {
            "original": "boazodoallo guovlu",
            "type": "msyn-compound",
            "explanation": "\"boazodoallo guovlu\" orru leamen goalloss\u00e1tni",
            "suggestion": [
              "boazodoalloguovlu"
            ]
          }
        }
      ]
    }
  }
}
```
