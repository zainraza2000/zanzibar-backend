from dataclasses import dataclass
from rococo.models import VersionedModel
from enum import Enum

class TodoStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"

@dataclass()
class Todo(VersionedModel):
    """A person organization role model."""

    person_id: str = None
    description: str = None
    status: TodoStatus = TodoStatus.PENDING.value