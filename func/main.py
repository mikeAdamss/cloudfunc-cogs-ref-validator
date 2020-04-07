
import json

from scanner import scan

def main(request):
    return json.dumps(scan())
