# aws-tools

A collection of tools to make working with AWS on the cli easier.

## Requirements

Note: this already assumes you have the AWS CLI and Python 3 installed and configured.

## Installation

```bash
pip install -r requirements.txt
```

This script also requires `dialog` to be installed on your system:
### MacOS

```bash
brew install dialog
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get install dialog
```

### Windows

Sorry, I don't know of a package for this. You can use WSL and install the Linux version.

## Usage

### aws-ecs-ssh
A tool that allows you to SSH into an AWS ECS container.
This script will prompt you to select a running ECS cluster, service, and task, and then it will SSH into the container.
```bash
python aws-ecs-ssh.py
```
