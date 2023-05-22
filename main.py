import time
import httpx
import re
import json
import uvicorn
from lxml.etree import HTML
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PAT = re.compile(r'window.initialState=(.+})', re.MULTILINE)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35'
}


@app.get("/items")
async def read_item(pageCallback: str = None):
    async with httpx.AsyncClient() as client:
        if not pageCallback:
            resp = await client.get("https://36kr.com/information/contact/", headers=headers, timeout=2)
            scripts = HTML(resp.content).xpath('//body/script/text()')
            if scripts:
                script = scripts[0]
                first_data_list = PAT.findall(script)
                for data_str in first_data_list:
                    data = json.loads(data_str)
                    information = data.get("information")
                    informationList = information.get("informationList")
        else:
            p_headers = dict(**headers)
            p_headers.setdefault('Content-Type', 'application/json')
            p_data = {
                "partner_id": "web",
                "timestamp": int(time.time() * 1000),
                "param": {
                    "subnavType": 1,
                    "subnavNick": "contact",
                    "pageSize": 30,
                    "pageEvent": 1,
                    "pageCallback": pageCallback,
                    "siteId": 1,
                    "platformId": 2
                }
            }
            resp = await client.post("https://gateway.36kr.com/api/mis/nav/ifm/subNav/flow",
                                     headers=p_headers, json=p_data)
            data = resp.json()
            informationList = data.get('data')
        return informationList

if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, host="127.0.0.1", port=8000)
