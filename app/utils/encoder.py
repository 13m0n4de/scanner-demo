import json

from typing import Dict, Union, List, Tuple
from pydantic import BaseModel, parse_obj_as
from dramatiq import DecodeError
from dramatiq.encoder import Encoder, MessageData

from app import models


class CustomJSONEncoder(Encoder):
    """基于默认 JSON 编码器修改，支持 pydantic 类型的序列化
    """

    def encode(self, data: MessageData) -> bytes:
        data = encode_pydantic_model(data)
        return json.dumps(data, separators=(",", ":")).encode("utf-8")

    def decode(self, data: bytes) -> MessageData:
        try:
            data_str = data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise DecodeError("failed to decode data %r" % (data,), data, e) from None

        try:
            data = json.loads(data_str)
            data = decode_pydantic_model(data)
            return data

        except AttributeError as e:
            raise DecodeError("cannot get pydantic model %r" % (data_str,), data_str, e) from e
        except json.decoder.JSONDecodeError as e:
            raise DecodeError("failed to decode message %r" % (data_str,), data_str, e) from e


def encode_pydantic_model(data) -> Union[Dict, List, Tuple]:
    if isinstance(data, BaseModel):
        model_dict = data.dict()
        model_dict['__pydantic_model__'] = data.__class__.__name__
        for field in data.__fields__:
            field_value = getattr(data, field)
            model_dict[field] = encode_pydantic_model(field_value)
        return model_dict

    elif isinstance(data, dict):
        return {k: encode_pydantic_model(v) for k, v in data.items()}

    elif isinstance(data, list):
        return list([encode_pydantic_model(item) for item in data])

    elif isinstance(data, tuple):
        return tuple((encode_pydantic_model(item) for item in data))

    else:
        return data


def decode_pydantic_model(data):
    if isinstance(data, dict) and '__pydantic_model__' in data:
        class_name = data['__pydantic_model__']
        _class = getattr(models, class_name)
        return parse_obj_as(_class, {k: decode_pydantic_model(v) for k, v in data.items()})

    elif isinstance(data, dict):
        return {k: decode_pydantic_model(v) for k, v in data.items()}

    elif isinstance(data, list):
        return list(decode_pydantic_model(item) for item in data)

    elif isinstance(data, tuple):
        return tuple((decode_pydantic_model(item) for item in data))

    else:
        return data

