from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime


class MessageCreate(BaseModel):
    """
    This class is used to create a message
    """

    content: str
    sender: str

    model_config = ConfigDict(from_attributes=True)


class MessageOut(MessageCreate):
    """
    This class is used to return a message
    """

    date: str

    @classmethod
    def model_validate(cls, message: any) -> any:
        formatted_date = message.date.strftime("%Y-%m-%d %H:%M:%S")
        return cls(
            content=message.content, sender=message.sender, date=formatted_date
        )
