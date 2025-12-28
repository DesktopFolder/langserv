from random import choice
from fastapi.responses import PlainTextResponse

from pydantic import BaseModel
from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import sys
from langdetect import detect

if 'dev' in sys.argv:
    print("In dev mode...")



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_words(lang: str):
    import os
    f = f'{lang}.json'
    if os.path.isfile(f):
        with open(f) as file:
            import json
            return json.load(file)
    return {}

def write_words(lang: str, d: dict):
    with open(f'{lang}.json', 'w') as file:
        import json
        json.dump(d, file, indent=2)

def take_once(w: dict, n: int):
    k = str(n)
    if k not in w:
        return None
    return w[k].pop(0)

@app.get("/poll", response_class=PlainTextResponse)
async def get_words():
    wfr = load_words("fr")
    wjp = load_words("jp")
    LINES = 5
    LOC = 0

    res: str = ""

    newfr = {}
    newjp = {}

    while LINES > 0:
        fr, jp = take_once(wfr, LOC), take_once(wjp, LOC)
        if fr is None and jp is None:
            break
        
        if fr is not None:
            LINES -= 1
            res += fr
            res += '\n'
            newfr[str(LOC + 1)] = fr

        if jp is not None:
            LINES -= 1
            res += jp
            res += '\n'
            newjp[str(LOC + 1)] = jp

    for k, v in newfr.items():
        if k not in wfr:
            wfr[k] = list()
        wfr[k].append(v)
    for k, v in newjp.items():
        if k not in wjp:
            wjp[k] = list()
        wjp[k].append(v)

    write_words("fr", wfr)
    write_words("jp", wjp)

    return res

class WordData(BaseModel):
    word: str

@app.post("/add")
async def add_words(word: WordData):
    lang = detect(word.word)
    print('Got language', lang, 'for word', word)
    # now do my own language detection lol
    if any(y.isascii() for y in word.word[0:3]):
        lang = 'fr'
    else:
        lang = 'jp'

    w = load_words(lang)
    if '0' not in w:
        w['0'] = list()
    w['0'].append(word.word)
    write_words(lang, w)
