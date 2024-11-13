Installation
Clone the repository - scripts to clone all access funding repositories available here

[Developer setup guide](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-setup.md)

Build Swagger & GovUK Assets
If the repo has static assets, it requires building it manually. Currently this step is required for frontend, authenticator & assessment repos.

This build step imports assets required for the GovUK template and styling components. It also builds customised swagger files which slightly clean the layout provided by the vanilla SwaggerUI 3.52.0 (which is included in dependency swagger-ui-bundle==0.0.9) are located at /swagger/custom/3_52_0.

Before first usage, the vanilla bundle needs to be imported and overwritten with the modified files. To do this run:

uv run python3 build.py

Developer note: If you receive a certification error when running the above command on macOS, consider if you need to run the Python 'Install Certificates.command' which is a file located in your globally installed Python directory. For more info see StackOverflow
