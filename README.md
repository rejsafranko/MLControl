# MLControl


[IN DEVELOPMENT] ❗❗❗
``` 
    __  _____    ______            __             __
   /  |/  / /   / ____/___  ____  / /__________  / /
  / /|_/ / /   / /   / __ \/ __ \/ __/ ___/ __ \/ / 
 / /  / / /___/ /___/ /_/ / / / / /_/ /  / /_/ / /  
/_/  /_/_____/\____/\____/_/ /_/\__/_/   \____/_/ 
``` 
MLControl is a command-line tool designed to help manage machine learning experiment workflows on Google Drive and Vast.ai. This tool allows you to create project directory templates and upload local data directories and training scripts to Google Drive effortlessly. It also wraps the Vast.ai CLI so you can rent a GPU, pull the data and scripts from Google Drive and run your model training scripts in a simple manner.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [Initialize a new MLOps project](#initialize-a-new-mlops-project)
  - [Upload local data directory](#upload-local-data-directory)
  - [List datasets or models in project directory](#list-datasets-or-models-in-project-directory)

## Features

- **Initialize MLOps Projects**: Create a structured project directory on Google Drive.
- **Upload Data**: Upload local data directories to your Google Drive project.
- **Connect to a GPU machine**: Search for and connect to GPUs offered by Vast.ai cloud services.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/rejsafranko/MLControl.git
    cd MLControl
    ```

2. **Install the CLI tool**:
    ```sh
    pip install -e .
    ```

## Setup

Before using `mlcontrol`, you need to set up Google Drive API credentials.

1. **Enable the Google Drive API**:
    - Go to the [Google Developers Console](https://console.developers.google.com/).
    - Create a new project or select an existing one.
    - Navigate to the "APIs & Services" > "Library".
    - Search for "Google Drive API" and enable it.

2. **Set up OAuth 2.0 credentials**:
    - Go to "APIs & Services" > "Credentials".
    - Click "Create Credentials" and select "OAuth client ID".
    - Configure the consent screen if prompted.
    - Select "Desktop app" and click "Create".
    - Download the JSON file and rename it to `credentials.json`.
    - Place the `credentials.json` file in the root directory of your project.

## Usage

### Initialize a new MLOps project

To initialize a new MLOps project on Google Drive:

```sh
mlcontrol init [PROJECT_NAME]
```

This command creates a new project directory with subdirectories data/ and models/.

### Upload local data directory
To upload a local data directory to an existing project on Google Drive:

```sh
mlcontrol upload [/path/to/local/data] [PROJECT_NAME] 
```

Replace /path/to/local/data with the path to your local data directory and provide the project name where you want to upload the data.

### List datasets or models in project directory
To list datasets or models in an existing project on Google Drive:

```sh
mlcontrol list [-d/-m] [PROJECT_NAME] 
```

-d argument is for datasets, -m argument is for models
