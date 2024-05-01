# proxygen-cli

## Installation

Installation is straightforward using pip:
```
pip install proxygen-cli
```
After installation, the `proxygen` executable is available. Typing `proxygen` displays a list of available commands.


## Configuration


### Settings
To specify the API you are developing for, use:
```
proxygen settings set api <API-NAME>
```
Your user must have the appropriate permissions for managing instances, secrets, and specifications related to the specified API. If permissions are insufficient, commands will fail. Reach out to the `platforms-api-producer-support` channel for assistance with permissions.


### Credentials
There are two ways to authenticate via the Proxygen CLI. Either via user login credentials such as a username and password or as a machine user using your private key and client_id.

#### Setting up for user access
If you are setting up user access for the first time you will first need to request a user account. Contact the [platforms-api-producer-support](https://nhsdigital-platforms.slack.com/archives/C016JRWN6AY) channel asking for a proxygen user account to be set up providing:

- Your nhs.net email address
- The proxygen-managed api/s your account will need access to

To setup the Proxygen CLI credentials for the first time with user access enter the following command:
```
proxygen credentials set
```
The CLI will ask you for your username, and password. These credentials will be securely stored on your local machine in the directory ~/.proxygen/credentials.yaml. The client_id and secret used for user access will be automatically added to this file after running the command.

Your user must have permissions to manipulate instances/secrets/specs for the API you set here. If you do not have sufficient permissions commands will fail. If you believe your permissions are incorrect, contact the API platform team via the [platforms-api-producer-support](https://nhsdigital-platforms.slack.com/archives/C016JRWN6AY) channel.

#### Setting up for machine-user access
After having set up your API using the instructions at [Getting set up with proxy generator](https://nhsd-confluence.digital.nhs.uk/display/APM/Getting+set+up+with+proxy+generator), you should have the following:

- A private key from a key pair for machine user access
- The key id for that specific key pair
- The client_id for your api machine user access (usually <your-api-name>-client)

Using this information enter the following command:
```
proxygen credentials set private_key_path <PATH_TO_PRIVATE_KEY> key_id <KEY_ID_FOR_PRIVATE_KEY> client_id <MACHINE_USER_CLIENT_ID>
```
The CLI will ask you for your username, and password. For machine authentication, the username and password must be left blank. The credentials will be securely stored in the directory ~/.proxygen/credentials.yaml.

> **_NOTE:_**  If you are switching between using user access and machine-user access bare in mind:
> - proxygen-cli will favour user access if username and password credentials are set
> - User access uses proxygen-cli-user-client as a client_id. If you switch between access modes remember to switch the client_id
> - The value for client_secret should remain untouched as it is not used for machine-user access
> - If you lose the client_secret for then proxygen-cli-user-client then reach out to the platforms-api-producer-support channel for it


## Commands
Commands are documented inside the CLI itself.
Type `proxygen` to see a full list of available commands.

For a full user guide for `proxygen-cli` see this [confluence page](https://nhsd-confluence.digital.nhs.uk/display/APM/Proxygen+CLI+user+guide).

### Deploying an API instance
To deploy an instance of an API you will need an OAS specification file. The OAS specification file can be deployed to an environment using the following command:
```
proxygen instance deploy <env> <base-path> path/to/specification.yaml
```
To manage your instances type `proxygen instance --help` for a list of available commands.

### Publishing an API sepcification
To publish your API specification, first deploy it on the UAT version of Bloomreach, then on production. Publishing to UAT allows you to preview the API documentation's appearance and catch any errors in the code before going live.

Use the following command to publish an API specification:
```
# Production
proxygen spec publish <path_to_spec>
 
# UAT
proxygen spec publish <path_to_spec> --uat
```
To manage your instances type `proxygen spec --help` for a list of available commands.

### Deploying a secret
The API key, considered sensitive information, is securely stored within the API platform as a 'secret'. Before configuring any instances reliant on this key, it's necessary to deploy it.

Use the following command to deploy a secret:
```
proxygen secret put <env> <apikey> --apikey --secret-file path/to/secret.txt
```
To manage your instances type `proxygen secret --help` for a list of available commands.

### Interacting with your docker repository
To enable the push and pull of images from the API Management ECR repository, you will need to acquire authentication details.

Use the following command to obtain a docker token:
```
$(proxygen docker get-login)
```
### Retrieving a token to use with the pytest-nhsd-apim python testing package
When testing using the pytest-nhsd-apim python testing package, an apigee management api token is needed. This endpoint provides this token for use in automated tests.

Use the following command to obtain the pytest-nhsd-apim token:
```
$(proxygen pytest_nhsd_apim get_token)
```