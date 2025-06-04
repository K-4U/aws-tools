import json
import os
import subprocess
import dialog

RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[m'

def do_aws_call(command):
    environ_copy = os.environ.copy()
    result = subprocess.run(
        f"aws {command} --output json --no-cli-pager",
        shell=True, text=True, capture_output=True, env=environ_copy
    )
    if result.returncode != 0:
        print(f"{RED}Failed to execute AWS command.{RESET}")
        print(result.stderr)
        exit(1)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"{RED}Failed to parse AWS command output.{RESET}")
        exit(1)

def read_clusters():
    clusters = do_aws_call("ecs list-clusters")
    clusters = [
        {
            "name": arn.split("/")[-1],
            "arn": arn,
        }
        for arn in clusters.get("clusterArns", [])
    ]
    if not clusters:
        print(f"{RED}No AWS clusters found. Are you connected to the right account?{RESET}")
        exit(1)
    return clusters

def read_services(cluster_arn):
    services = do_aws_call(f"ecs list-services --cluster {cluster_arn}")
    return [
        {
            "name": arn.split("/")[-1],
            "arn": arn,
        }
        for arn in services.get("serviceArns", [])
    ]

def read_tasks(cluster_arn, service_arn):
    tasks = do_aws_call(f"ecs list-tasks --cluster {cluster_arn} --service-name {service_arn}")
    return [
        {
            "name": arn.split("/")[-1],
            "arn": arn,
        }
        for arn in tasks.get("taskArns", [])
    ]

def read_containers(cluster_arn, task_arn):
    task = do_aws_call(f"ecs describe-tasks --cluster {cluster_arn} --tasks {task_arn}")
    if not task or "tasks" not in task or not task["tasks"]:
        print(f"{RED}No tasks found for the given cluster and task ARN.{RESET}")
        exit(1)
    containers = task["tasks"][0].get("containers", [])
    if not containers:
        print(f"{RED}No containers found in the task.{RESET}")
        exit(1)
    return [
        {
            "name": container["name"],
            "arn": container["containerArn"],
        } for container in containers
    ]

def build_choices(items, key="name"):
    return [(str(i), item[key]) for i, item in enumerate(items)]

def select_menu(dialog_instance, title, items):
    choices = build_choices(items)
    button, choice = dialog_instance.menu(title, choices=choices)
    if button != "ok":
        exit(0)
    return items[int(choice)]

def main():
    my_dialog = dialog.Dialog(dialog="dialog", autowidgetsize=True)
    my_dialog.set_background_title("ECS Cluster Selector")

    clusters = read_clusters()
    selected_cluster = select_menu(my_dialog, "Choose an ECS Cluster", clusters)

    services = read_services(selected_cluster["arn"])
    selected_service = select_menu(my_dialog, "Choose a service", services)

    tasks = read_tasks(selected_cluster["arn"], selected_service["arn"])
    if not tasks:
        print(f"{RED}No tasks found for the selected service.{RESET}")
        exit(1)
    selected_task = tasks[0] if len(tasks) == 1 else select_menu(my_dialog, "Choose a task", tasks)

    containers = read_containers(selected_cluster["arn"], selected_task["arn"])
    if not containers:
        print(f"{RED}No containers found for the selected task.{RESET}")
        exit(1)
    selected_container = containers[0]["name"] if len(containers) == 1 else select_menu(my_dialog, "Choose a container", containers)["name"]

    os.system("clear")
    os.system(
        f"aws ecs execute-command --cluster {selected_cluster['arn']} "
        f"--container {selected_container} --task {selected_task['arn']} "
        "--command '/bin/bash' --interactive"
    )

if __name__ == "__main__":
    main()
