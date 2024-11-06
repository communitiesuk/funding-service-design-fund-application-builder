Installation
Clone the repository - scripts to clone all access funding repositories available here

Create a Virtual environment
    python3 -m venv .venv
Enter the virtual environment
...either macOS using bash:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

Install dependencies
From the top-level directory enter the command to install pip and the dependencies of the project

    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

NOTE: requirements-dev.txt and requirements.txt are updated using pip-tools pip-compile. To update requirements please manually add the dependencies in the .in files (not the requirements.txt files) Then run:

    pip-compile requirements.in

    pip-compile requirements-dev.in

Build Swagger & GovUK Assets
If the repo has static assets, it requires building it manually. Currently this step is required for frontend, authenticator & assessment repos.

This build step imports assets required for the GovUK template and styling components. It also builds customised swagger files which slightly clean the layout provided by the vanilla SwaggerUI 3.52.0 (which is included in dependency swagger-ui-bundle==0.0.9) are located at /swagger/custom/3_52_0.

Before first usage, the vanilla bundle needs to be imported and overwritten with the modified files. To do this run:

python3 build.py

Developer note: If you receive a certification error when running the above command on macOS, consider if you need to run the Python 'Install Certificates.command' which is a file located in your globally installed Python directory. For more info see StackOverflow
