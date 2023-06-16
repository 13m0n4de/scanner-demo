import json

from pydantic import BaseModel, parse_obj_as
from dramatiq import DecodeError
from dramatiq.encoder import Encoder, MessageData

from app import models


class CustomJSONEncoder(Encoder):
    """基于默认 JSON 编码器修改，支持 pydantic 类型的序列化
    """

    def encode(self, data: MessageData) -> bytes:
        # 判断传参是不是 pydantic model，如果是转换成 Dict
        # 并且在里面添加累名用来反序列化
        if isinstance(data['args'][0], BaseModel):
            args_dict = data['args'][0].dict()
            args_dict['__pydantic_model__'] = data['args'][0].__class__.__name__
            if len(data['args']) == 1:
                data['args'] = (args_dict,)
            else:
                data['args'] = (args_dict, data['args'][1:])
        return json.dumps(data, separators=(",", ":")).encode("utf-8")

    def decode(self, data: bytes) -> MessageData:
        try:
            data_str = data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise DecodeError("failed to decode data %r" % (data,), data, e) from None

        try:
            data = json.loads(data_str)
            # 判断参数是不是字典，如果是且有 __pydantic_model 字段，说明是 pydantic 的 model
            # 通过 getattr 配合类名获取 models 里的类，用 parse_obj_as 转换至 model
            if isinstance(data['args'][0], dict):
                if class_name := data['args'][0].get('__pydantic_model__'):
                    _class = getattr(models, class_name)
                    model = parse_obj_as(_class, data['args'][0])

                    if len(data['args']) == 1:
                        data['args'] = model,
                    else:
                        data['args'] = model, data['args'][1:]
            return data

        except AttributeError as e:
            raise DecodeError("cannot get pydantic model %r" % (data_str,), data_str, e) from e
        except json.decoder.JSONDecodeError as e:
            raise DecodeError("failed to decode message %r" % (data_str,), data_str, e) from e
