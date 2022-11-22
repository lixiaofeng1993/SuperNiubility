#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: jwt_sign.py
# 说   明: 
# 创建时间: 2021/12/26 23:27
# @Version：V 0.1
# @desc :
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from public.conf import SECRET_KEY, ALGORITHM
from public.log import logger


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError as error:
        logger.error(f"解析token - JWTError报错 ===>>> {error}")
        return {"jwt": error}
    except Exception as error:
        logger.error(f"解析token报错 ===>>> {error}")
        return {"error": error}


if __name__ == '__main__':
    print(create_access_token({"sub": "lixiaofeng"}))
