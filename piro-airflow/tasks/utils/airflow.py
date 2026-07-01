def get_task_instance(context):
    """Retrieve the task instance for the currently running task."""
    task_instance = context.get("ti")
    if task_instance is None:
        raise Exception("Task instance is missing from context")

    return task_instance
