# Copyright (c) 2018 Viktor Vorobjov
from aiohttp import web
import os
import json
import datetime
import hashlib
import logging

access_logger = logging.getLogger('aiohttp.access')
log = logging.getLogger('ota_server')
logging.basicConfig(level=logging.DEBUG)

import sys
print(sys.path)



async def test(request):
    print('Handler function called')
    return web.Response(text="Hello")

@web.middleware
async def logger_factory(request, handler):
    log.debug('Response: \n m: {}\n p:{}'.format(request.method, request.path))
    response = await handler(request)
    return response

app = web.Application(middlewares=[logger_factory])

app.router.add_get('/', test)

PORT = 8080
partfile = 'ota.bin'
vfsfile = 'ota.tar'
chunk_sz = 512
#otahost = "http://192.168.100.173:8080"
otahost = "http://192.168.10.113:8080"

def get_update(res, board, f_type, f_part):

    otahost_url = '{}/chunk/{}/{}'.format(otahost, board, f_type, f_part)
    f_pth = "./boards/{}/{}".format(board, f_part)

    try:
        f_size = int(os.stat(f_pth).st_size)
    except Exception as e:
        log.error(e)
        f_size = False

    if f_size:
        f_sha = hashlib.sha256(open(f_pth, 'rb').read()).hexdigest()
        p_arg = f_type
        if p_arg == "part":
            p_arg = 'partition'

        res['update'][p_arg] = {'url': otahost_url, 'size': f_size, 'hash': f_sha}


async def updatemeta(request):
    res = {}
    res['update'] = {}
    board = request.match_info['board']

    log.info('Board: {}'.format(board))

    get_update(res, board, "part", partfile)
    get_update(res, board, "vfs", vfsfile)
    res_q = json.dumps(res)

    log.debug('Request Json: {}'.format(res_q))

    return web.json_response(res_q)


app.router.add_get('/updatemeta/{board}', updatemeta)


async def download_file(request):

    type = request.match_info['type']
    board = request.match_info['board']

    headers = {}

    id_seek = None
    if 'id' in request.match_info and request.match_info['id'].isdigit():
        id_seek = int(request.match_info['id'])
        headers["Transfer-Encoding"] = "chunked"

    path = None

    if type == 'part':
        path = partfile
    elif type == 'vfs':
        path = vfsfile

    path = "./boards/{}/{}".format(board, path)

    headers = {
        "Content-disposition": "attachment; filename={file_name}".format(file_name=path)
    }

    file_path = os.path.realpath(path)

    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_name}> does not exist'.format(file_name=path),
            status=404
        )

    resp = web.StreamResponse(headers=headers)

    await resp.prepare(request)

    with open(file_path, 'rb') as f:
        if id_seek is not None:
            f.seek(chunk_sz * id_seek)

        chunk = f.read(chunk_sz)
        while chunk:
            await resp.write(chunk)
            chunk = f.read(chunk_sz)

app.router.add_get('/chunk/{board}/{type}/{id}', download_file)
app.router.add_get('/chunk/{board}/{type}/', download_file)


web.run_app(app=app, access_log=access_logger, port=PORT)


