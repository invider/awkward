# awkward

On-demand zero-maintenance awk-powered database engine.

You can start a database server in any unix folder
and serve the content over the network.

The query language is powered by *awk* under the hood.

# How to generate SSL certificates

create CA authority first:

```bash
cd cert
./createCA
```

Now generate the certiciate:
```bash
./generate
```

Configure the server to run with the generated *awkward.crt*.

CA Authority is specified by ./cert/awkwardCA.pem.
Include that file in the trusted certification authority list in the browser,
or as a verify option in the SSL client.

