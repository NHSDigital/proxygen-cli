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

All users should have individual credentials.
`proxygen-cli` needs to know about them.

```
proxygen credentials set username <USERNAME>
proxygen credentials set password <PASSWORD>
```

The CLI has its own client credentials, which need to be input.
Contact `deathstar` squad or the `platforms-api-producer-support` slack channel to find out what they are.
```
proxgen credentials set client_id <CLIENT_ID>
proxgen credentials set client_secret <CLIENT_SECRET>
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
