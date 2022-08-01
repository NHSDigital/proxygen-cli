# Proxygen CLI
Proxygen CLI is a command line interface to interact with the [proxygen service](https://proxygen.ptl.api.platform.nhs.uk/docs).

[What is PaaS/Proxygen?](https://nhsd-confluence.digital.nhs.uk/display/APM/Platform+as+a+service+-+PaaS)

## Getting started

Run the install script to install proxygen-cli.
```bash
curl -o- https://raw.githubusercontent.com/NHSDigital/proxygen-cli/main/install.sh | bash
```

Check proxygen is installed by running the command ```proxygen```

Setup authentication. You will then be prompted for your login details.
```bash
proxygen setup-user
```

Check you are authenticated
```bash
proxygen check
```

## Deploy an API
First navigate to your repo with your `instance.json` defined

Use ```plan``` to preview the updates to be applied
```bash
proxygen plan --api-name=<api-name> 
```

Use ```apply``` to update your api
```bash
proxygen apply --api-name=<api-name> 
```

## Example Use Cases
Get a PaaS bearer token so you can call the PaaS API directly.
```bash
curl https://proxygen.ptl.api.platform.nhs.uk/apis/hello-world -H "Authorization: $(proxygen get-token)"
```

Upload your API spec
```bash
curl -X POST https://proxygen.ptl.api.platform.nhs.uk/apis/hello-world/spec \
          -H "Authorization: $(proxygen get-token)" \
          -H 'Content-Type: application/json' \
          -d @hello-world.json
```

Login with docker so you can push and pull from the APIM ECR repo.
```bash
proxygen docker-login | bash  # Login lasts 12 hours
```

Setup authentication as a machine user for using proxygen in a pipeline.
```bash
proxygen setup-machine-user --client-id=<client-id> --private-key=<pathtofile>
```

## Uninstall
```bash
~/.paas/uninstall.sh
```
