from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Cats API",
    description="A simple FastAPI app using JSON as a database, demonstrating GET, POST, PUT, DELETE and HTML response.",
    version="1.0.0"
)

# Always resolve data.json relative to this file
DATA_FILE = Path(__file__).parent / "data.json"

def read_data():
    """Read JSON file and return its contents."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error reading JSON file:", e)
        return {"cats": []}

def write_data(data):
    """Write data back to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Cat(BaseModel):
    code: int
    name: str
    message: str
    image_url: str = None

@app.get("/cats", response_model=list[Cat])
def list_cats():
    """Return all cats from data.json."""
    data = read_data()
    return data["cats"]

@app.get("/cats/{code}", response_model=Cat)
def get_cat(code: int):
    """Return a single cat by its code."""
    data = read_data()
    for cat in data["cats"]:
        if cat["code"] == code:
            return cat
    raise HTTPException(status_code=404, detail="Cat not found")

@app.post("/cats", response_model=Cat)
def add_cat(cat: Cat):
    """Add a new cat to the JSON file."""
    data = read_data()
    if any(c["code"] == cat.code for c in data["cats"]):
        raise HTTPException(status_code=400, detail="Cat code already exists")
    data["cats"].append(cat.dict())
    write_data(data)
    return cat

@app.put("/cats/{code}", response_model=Cat)
def update_cat(code: int, cat: Cat):
    """Update an existing cat identified by its code."""
    data = read_data()
    for idx, c in enumerate(data["cats"]):
        if c["code"] == code:
            data["cats"][idx] = cat.dict()
            write_data(data)
            return cat
    raise HTTPException(status_code=404, detail="Cat not found")

@app.delete("/cats/{code}")
def delete_cat(code: int):
    """Delete a cat by its code."""
    data = read_data()
    for idx, c in enumerate(data["cats"]):
        if c["code"] == code:
            deleted = data["cats"].pop(idx)
            write_data(data)
            return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Cat not found")

@app.get("/cats/{code}/image", response_class=HTMLResponse)
def show_cat_image(code: int):
    """
    Show an HTML page with the cat image embedded.
    This demonstrates returning HTML instead of JSON.
    """
    data = read_data()
    for cat in data["cats"]:
        if cat["code"] == code and cat.get("image_url"):
            return f"""
            <html>
              <head><title>{cat['name']}</title></head>
              <body style='text-align:center; font-family:sans-serif;'>
                <h1>{cat['name']} ({cat['code']})</h1>
                <p>{cat['message']}</p>
                <img src="{cat['image_url']}" alt="cat image" style="max-width:80%; height:auto;" />
              </body>
            </html>
            """
    raise HTTPException(status_code=404, detail="Cat not found or no image URL")