class TaskAgent:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_description):
        self.tasks.append({"description": task_description, "completed": False})
        return f"Task added: {task_description}"

    def list_tasks(self):
        if not self.tasks:
            return "No tasks available."

        result = "Current tasks:\n"
        for i, task in enumerate(self.tasks, 1):
            status = "✓" if task["completed"] else "○"
            result += f"{i}. {status} {task['description']}\n"
        return result

    def complete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed"] = True
            return f"Completed task: {self.tasks[task_index]['description']}"
        return "Invalid task index"

def main():
    agent = TaskAgent()

    # Add some sample tasks
    print(agent.add_task("Set up development environment"))
    print(agent.add_task("Create project structure"))
    print(agent.add_task("Implement basic features"))

    # List tasks
    print(agent.list_tasks())

    # Complete a task
    print(agent.complete_task(0))

if __name__ == "__main__":
    main()