import uuid

from dramatiq import Message, pipeline

EXTERNAL_JOB_STORE = {}


class StoredPipeline(pipeline):
    def __init__(self, children=None, broker=None, job_id=None):
        self.job_id = str(uuid.uuid4())

        if job_id:
            children = self.restore_pipeline(job_id)
            self.job_id = job_id

        super().__init__(children, broker=broker)

    def store_pipeline(self):
        job = [msg.asdict() for msg in self.messages]
        EXTERNAL_JOB_STORE[self.job_id] = job
        return self.job_id

    @staticmethod
    def restore_pipeline(job_id):
        messages = []

        for message in EXTERNAL_JOB_STORE[job_id]:
            messages.append(
                Message(
                    queue_name=message["queue_name"],
                    actor_name=message["actor_name"],
                    args=message["args"],
                    kwargs=message["kwargs"],
                    options=message["options"],
                    message_id=message["message_id"],
                    message_timestamp=message["message_timestamp"],
                )
            )

        return messages

    def get_id(self):
        return self.job_id
