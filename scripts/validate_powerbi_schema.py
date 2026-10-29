"""Check PBIR schemas from Microsoft; requires jsonschema and internet access."""
from functools import lru_cache
import json
from pathlib import Path
from urllib.request import urlopen
from jsonschema.validators import validator_for
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=None)
def fetch(uri):
    if not uri.startswith('https://developer.microsoft.com/json-schemas/fabric/item/'):
        raise ValueError(f'Unexpected schema URL: {uri}')
    with urlopen(uri, timeout=30) as stream:
        return json.load(stream)

def retrieve(uri):
    return Resource.from_contents(fetch(uri))

if __name__ == '__main__':
    registry = Registry(retrieve=retrieve)
    count = 0
    for path in sorted((ROOT/'powerbi').rglob('*')):
        if not path.is_file() or path.suffix not in {'.json','.pbir','.pbism'}:
            continue
        doc = json.loads(path.read_text())
        if '$schema' not in doc:
            continue
        schema = fetch(doc['$schema'])
        validator_for(schema)(schema, registry=registry).validate(doc)
        count += 1
    print(json.dumps({'schema_documents':count, 'result':'passed', 'source':'Microsoft published JSON schemas', 'scope':'PBIR and definition properties only; excludes model.bim semantics and Desktop runtime'}))
