import requests
from fastapi import FastAPI, Request, Response
from lxml import etree

app = FastAPI()


@app.delete("/library/metadata/{item_id}")
async def delete_item(item_id: str, request: Request):
    # 1. 把原始 Plex 请求的 headers 和 querystring 拿到
    headers = dict(request.headers)
    query_params = dict(request.query_params)

    # 2. 请求 Plex API 获取 XML 信息
    plex_url = f"{PLEX_SERVER}/library/metadata/{item_id}"
    plex_resp = requests.get(plex_url, headers=headers, params=query_params)

    if plex_resp.status_code != 200:
        return Response(
            content="Failed to fetch metadata",
            status_code=plex_resp.status_code,
        )

    # 3. 解析 XML 文件
    xml_root = etree.fromstring(plex_resp.content)
    part = xml_root.find(".//Part")
    file_path = part.get("file") if part is not None else None

    # 4. 发送到 webhook
    if file_path:
        requests.post(WEBHOOK_URL, json={"id": item_id, "file": file_path})

    # 5. 把删除请求继续发给 Plex，并返回它的响应
    delete_url = f"{PLEX_SERVER}/library/metadata/{item_id}"
    delete_resp = requests.delete(
        delete_url, headers=headers, params=query_params
    )

    return Response(
        content=delete_resp.content,
        status_code=delete_resp.status_code,
        media_type=delete_resp.headers.get("Content-Type"),
    )
