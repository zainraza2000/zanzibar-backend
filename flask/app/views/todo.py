from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, get_failure_response, parse_request_body, validate_required_fields
from common.app_config import config
from common.services import TodoService
from common.models.todo import Todo, TodoStatus
from app.helpers.decorators import login_required

todo_api = Namespace('todo', description="Todo-related APIs")

@todo_api.route('/')
class Todos(Resource):
    
    @login_required()
    def get(self, person):
        """Get todos for the authenticated person"""
        status_params = request.args.get('status', 'pending,complete').split(',')
        try:
            statuses = [TodoStatus(status_param.lower()).value for status_param in status_params]
        except ValueError:
            valid_values = ', '.join([s.value for s in TodoStatus])
            return get_failure_response(message=f"Invalid status: {status_params}. Valid values are: {valid_values}")
        
        todo_service = TodoService(config)
        todos = todo_service.get_todos_by_person_id_by_status(person.entity_id, statuses)
        return get_success_response(todos=[todo.as_dict() for todo in todos])

    @login_required()
    @todo_api.expect(
        {'type': 'object', 'properties': {
            'description': {'type': 'string'},
            'status': {'type': 'string', 'enum': ['pending', 'complete']}
        }}
    )
    def post(self, person):
        """Create a new todo for the authenticated person"""
        required_body = parse_request_body(request, ['description'])
        parsed_body = parse_request_body(request, ['description', 'status'])
        validate_required_fields(required_body)
        
        status_str = parsed_body.get('status', 'pending')
        try:
            status = TodoStatus(status_str).value
        except ValueError:
            valid_values = ', '.join([s.value for s in TodoStatus])
            return get_failure_response(message=f"Invalid status: {status_str}. Valid values are: {valid_values}")
        
        todo = Todo(
            person_id=person.entity_id,
            description=parsed_body['description'],
            status=status
        )
        
        todo_service = TodoService(config)
        saved_todo = todo_service.save_todo(todo)
        
        return get_success_response(message="Todo created successfully.", todo=saved_todo.as_dict())


@todo_api.route('/<string:todo_id>')
class TodoItem(Resource):
    
    @login_required()
    @todo_api.expect(
        {'type': 'object', 'properties': {
            'description': {'type': 'string'},
            'status': {'type': 'string', 'enum': ['pending', 'complete']}
        }}
    )
    def put(self, todo_id, person):
        """Update an existing todo"""
        parsed_body = parse_request_body(request, ['description', 'status'], default_value=None)
        
        if not any(parsed_body.values()):
            return get_failure_response(message="Request body cannot be empty. Please provide at least one field to update (description or status)")
        
        todo_service = TodoService(config)
        
        existing_todo = todo_service.todo_repo.get_one({"entity_id": todo_id})
        if not existing_todo:
            return get_failure_response(message="Todo not found", status_code=404)
        
        if existing_todo.person_id != person.entity_id:
            return get_failure_response(message="Unauthorized access to todo", status_code=403)
        
        if parsed_body['description'] is not None:
            existing_todo.description = parsed_body['description']
        
        if parsed_body['status'] is not None:
            status_str = parsed_body['status']
            try:
                status = TodoStatus(status_str).value
                existing_todo.status = status
            except ValueError:
                return get_failure_response(message=f"Invalid status: {status_str}. Valid values are: pending, complete")
        
        saved_todo = todo_service.save_todo(existing_todo)
        
        return get_success_response(message="Todo updated successfully.", todo=saved_todo.as_dict())

    @login_required()
    def delete(self, todo_id, person):
        """Delete a todo"""
        todo_service = TodoService(config)
        
        existing_todo = todo_service.todo_repo.get_one({"entity_id": todo_id})
        if not existing_todo:
            return get_failure_response(message="Todo not found", status_code=404)
        
        if existing_todo.person_id != person.entity_id:
            return get_failure_response(message="Unauthorized access to todo", status_code=403)
        
        deleted_todo = todo_service.delete_todo(todo_id)
        
        return get_success_response(message="Todo deleted successfully.", todo=deleted_todo.as_dict())
