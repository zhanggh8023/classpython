"""
# -------------------------------
# @Time    : 2021/4/21 10:31
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : zgh_main.py
# -------------------------------
"""


from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/item/{item_id}")
def get_item(item_id: int, q: str=None):
    return {"item": item_id, "q": q}


@app.put("/item/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item_name": item.name}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8080)
