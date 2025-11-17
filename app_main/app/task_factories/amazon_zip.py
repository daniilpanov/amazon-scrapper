from pydantic import BaseModel

from .abstract_factory import AbstractFactory


class AmazonZipTask(BaseModel):
    zipCode: int


class AmazonZipFactory(AbstractFactory):
    def publish_amazon_zip_task(self):
        self._basic_publish(exchange="tasks", routing_key="amazon-zip", body=AmazonZipTask(zipCode=90005))
