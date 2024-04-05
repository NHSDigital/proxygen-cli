# proxygen-cli

## Installation

Installation is straightforward using pip:
```
pip install proxygen-cli
```
After installation, the `proxygen` executable is available. Typing `proxygen` displays a list of available commands.


## Configuration

### Credentials

The CLI requires client credentials, which can be obtained from the `platforms-api-producer-support` Slack channel.

All users should also have individual credentials. `proxygen-cli` needs to know about them.
You can setup the credentials in `proxygen-cli` using:
```
proxygen credentials set
```
This command prompts you to enter your `client_id`, `client_secret`, `username`, and `password`. 
To update credentials in the future, use:
```
proxygen credentials set <KEY> <VALUE>
```


### Settings
To specify the API you are developing for, use:
```
proxygen settings set api <API-NAME>
```
Your user must have the appropriate permissions for managing instances, secrets, and specifications related to the specified API. If permissions are insufficient, commands will fail. Reach out to the `platforms-api-producer-support` channel for assistance with permissions.


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