# BudgetLens
>
> [!NOTE]
> Copyright 2024 - present [Ioannis Theodosiadis](mailto:ioannis@seoultech.ac.kr), SEOULTECH University
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> at your option any later version
>
> This program is distributed in the hope that it will be useful
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details
>
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <https://www.gnu.org/licenses/>
>
> Preview this Markdown file in VS Code with <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd>

---

- BudgetLens is the open-source receipt scanner and expense tracker made for self-hosting.
- This is a Django App using the OpenAI API for image recognition and categorization.
- The data is stored in a PostgreSQL DB and images are stored on the Linux filesystem.
- The UI is made with the static build-in templating engine of Django.

---

## Contents

- [Local Installation](#local-installation)
- [Initialization](#initialization)
- [Application Start](#application-start)

## Local Installation
>
> [!NOTE]
> A [Python](https://www.python.org/downloads/) installation of the version 3.12 is required to run this project.

1. First create a python virtual environment in the root directory:

    ```PowerShell
    python -m venv .venv
    ```

1. Activate the venv:

    - Windows:

        ```PowerShell
        .\venv\Script\activate
        ```

    - Mac / Linux:

        ```bash
        source myenv/bin/activate
        ```

1. Upgrade pip if necessary:

    ```PowerShell
    python -m pip install --upgrade pip
    ```

1. Install the required dependencies:

    ```PowerShell
    pip install -r requirements.txt
    ```

## Initialization

After the basic installation, you have to initialize the Django App and DB properly. First we need to start the DB. In order to get started easy, I have provided a docker compose script in `.extras/compose` for the DB.

> [!NOTE]
> This step requires at minimum a [Docker Engine](https://docs.docker.com/engine/install) installation.

1. **Start the DB:**

    In a terminal execute the following prompts.

    ```PowerShell
    cd .\.extras\compose
    ```

    ```PowerShell
    docker compose up
    ```

1. **Setup environment variables:**

    In another terminal window execute the following steps.

    - You need to create a `.env` file in the `budgetlens` directory.

        ```PowerShell
        cd budgetlens
        ```

        - Windows:

            ```PowerShell
            New-Item -ItemType File -Name ".env"
            ```

        - Mac / Linux:

            ```PowerShell
            touch .env
            ```

    - Within this file you have to specify the following env variables:

        ```dotenv
        DB_NAME=budgetlens
        DB_USER=postgres
        DB_PASSWORD=postgres
        DB_HOST=127.0.0.1
        DB_PORT=5432

        ALLOWED_HOSTS=127.0.0.1,localhost

        OPENAI_API_KEY={insert your own API key here}
        OPEN_EXCHANGE_RATES_API_KEY={insert your own API key here}
        PREFERRED_CURRENCY=EUR
        ```

        > ❗**Important**
        >
        > Keep in mind, these are only example variables. Never ever upload or expose them to the public.
        > Be especially careful with API keys.

1. **Migrate the DB:**

    > ❗**Important**
    >
    > The Python `venv` has to be activated for these steps.

    In another terminal window execute the following prompts.

    ```PowerShell
    cd budgetlens
    ```

    ```PowerShell
    python manage.py makemigrations
    ```

    ```PowerShell
    python manage.py migrate
    ```

1. **Create a superuser for Django Admin:**

    Try not to forget the credentials you will create.

    ```PowerShell
    python manage.py createsuperuser
    ```

## Application Start

Now that we are all setup, it is time to start the application.

```PowerShell
python manage.py runserver
```

<!-- TODO Continue here-->
