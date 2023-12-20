# proxygen-cli

## Installation

Should be as simple as
```
pip install proxygen-cli
```
The python package includes an execuatable `proxygen`.
Type `proxygen` to see a list of available commands.


## Configuration

### Credentials

The CLI has its own client credentials, which need to be input.
Contact `deathstar` squad or the `platforms-api-producer-support` slack channel to find out what they are.

All users should also have individual credentials. `proxygen-cli` needs to know about them.

Simply execute the following command which will prompt you to enter your `client_id`, `client_secret`, `username`, and `password`:
```
proxygen credentials set
```

If you need to update any credentials in the future, use the following command:
```
proxygen credentials set <KEY> <VALUE>
```


### Settings
`proxygen-cli` needs to know what API you are developing.

```
proxygen settings set api <API-NAME>
```
Your user must have permissions to manipulate instances/secrets/specs for the API you set here.
If you do not have sufficient permissions commands will fail.
If you believe your permissions are incorrect, contact the `platforms-api-producer-support` channel.

## Commands
Commands are documented inside the CLI itself.
Type `proxygen` to see a list of available commands.
