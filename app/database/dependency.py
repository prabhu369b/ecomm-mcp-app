from fastapi import Request

def get_mongo(
        
    request: Request
):
    return request.app.state.mongo

def get_redis(
        request: Request
):
    return request.app.state.redis