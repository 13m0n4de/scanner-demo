import uuid

from redis import StrictRedis
from dramatiq import Message, pipeline

from app.config import CONFIG
from app.utils import CustomJSONEncoder


class StoredPipeline(pipeline):
    def __init__(
        self, children=None, broker=None, job_id=None, encoder=CustomJSONEncoder()
    ):
        self.job_id = str(uuid.uuid4())
        self.redis = StrictRedis(
            host=CONFIG["redis"]["host"],
            port=CONFIG["redis"]["port"],
            db=CONFIG["redis"]["db"],
        )
        self.encoder = encoder

        if job_id:
            children = self.restore_pipeline(job_id)
            self.job_id = job_id

        super().__init__(children, broker=broker)

    def store_pipeline(self):
        pipeline_key = f"myapp:pipelines:{self.job_id}"

        for message in self.messages:
            message_data = self.encoder.encode(message.asdict())
            self.redis.rpush(pipeline_key, message_data)

        return self.job_id

    def restore_pipeline(self, job_id):
        pipeline_key = f"myapp:pipelines:{job_id}"
        pipeline_data = self.redis.lrange(pipeline_key, 0, -1)
        messages = []

        if pipeline_data:
            for message in pipeline_data:
                message_data = self.encoder.decode(message)
                messages.append(
                    Message(
                        queue_name=message_data["queue_name"],
                        actor_name=message_data["actor_name"],
                        args=message_data["args"],
                        kwargs=message_data["kwargs"],
                        options=message_data["options"],
                        message_id=message_data["message_id"],
                        message_timestamp=message_data["message_timestamp"],
                    )
                )

        return messages

    def get_id(self):
        return self.job_id
