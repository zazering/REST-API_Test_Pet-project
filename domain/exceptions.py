class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id: {task_id} now found")

    def TaskValidationError(Exception):
        pass
