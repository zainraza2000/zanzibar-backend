from common.repositories.factory import RepositoryFactory, RepoType
from common.models.todo import TodoStatus, Todo

class TodoService:
    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.todo_repo = self.repository_factory.get_repository(RepoType.TODO)
    
    def get_todos_by_person_id_by_status(self, person_id: str, statuses: list[TodoStatus] = [TodoStatus.PENDING.value]):
        todos = self.todo_repo.get_many({"person_id": person_id, "status": statuses})
        return todos
    
    def save_todo(self, todo: Todo):
        todo = self.todo_repo.save(todo)
        return todo
    
    def delete_todo(self, todo_id: str):
        todo = self.todo_repo.get_one({"entity_id": todo_id})
        if not todo:
            return None
        self.todo_repo.delete(todo)
        return todo
    
