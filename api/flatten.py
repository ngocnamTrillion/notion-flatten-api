from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
NOTION_BASE = "https://api.notion.com/v1"

class PageInput(BaseModel):
    page_id: str

def extract_text(block):
    text = ""
    data = block.get(block["type"], {})
    for rt in data.get("rich_text", []):
        if rt.get("type") == "text":
            text += rt["text"]["content"]
    return text.strip()

def get_all_text_recursive(block_id):
    texts = []
    url = f"{NOTION_BASE}/blocks/{block_id}/children?page_size=100"
    while url:
        res = requests.get(url, headers=headers)
        data = res.json()
        for block in data.get("results", []):
            txt = extract_text(block)
            if txt:
                texts.append(txt)
            if block.get("has_children"):
                texts += get_all_text_recursive(block["id"])
        url = None
    return texts

@app.post("/api/flatten")
def flatten_blocks(req: PageInput):
    return get_all_text_recursive(req.page_id)
