# awkward

On-demand zero-maintenance awk-powered database engine.

You can start a database server in any unix folder
and serve the content over the network.

The query language is powered by *awk* and other unix tools under the hood.

# Design

Most of the modern database management systems are highly sophisticated
and performant pieces of technology. They are marvels of software engineering,
applying the most optimized algorithms and data structures
to process and store enourmous amounts of information.

These systems are fighter jets of data handling.
And, as a modern fighter jet, any such system costs a lot.
It needs a highly skilled maintenance crew and pilot,
it needs expensive spare parts,
and it burns a lot of jet fuel.

But what if you don't need a fighter jet, and all you need is a cheap unicycle.
Maybe your use case doesn't require enormous power and needs just a simple
data access solution that is super-easy to install, run and maintain.
**Awkward** tries to fill the niche. *It is a unicycle of database engines.*

Once I had the need to aggregate data from multiple log files on my server.
The industrial-strength solution would be to deploy log aggregation system
like ELK or similar. But it is an overkill for my case.
Another option is to deploy a local lightweight DBMS (like LiteSQL)
and then import and request data from there. This also seems to be quite complex.

It is also quite easy to expose those files over HTTP just by starting
python simple http server in the logs folder.
But in this scenario we would have to load potentially big log files
over the network and aggregate them on the client side.

As a regular UNIX junkie, I just connected to that server over ssh
and used powerful UNIX toolbox (grep/sed/awk/sort/unique...)
to aggregate the log data on local filesystem.
But what if I can do the same with web-native tools
over http/https protocols without the need to connect over the ssh?
That is how idea of **awkward** was born.

Lets deliver the power of *awk* and other unix utils over the web
with a simple drop-script you can deploy in seconds.


# Security

There might be lot of concerns about security once you start exposing
the power of unix shell to the web.
It is almost like openly publish ssh credentials,
so some threats MUST be considered.

Never expose **awkward** port to the Internet.
It is a sketch/test/debug tool for fast mock-ups
and it's not intended for production use.

Consider the usage over https with access token
to restrict the access.
Also, you can bind the port to particular IP
your clients are going to connect from.

Since the main use case is a fast and convenient access
to log file data and the such,
the most dangerous is the potential ability
to access files outside the exposed folder.

To aleviate this, consider running **awkward** as a highly restricted user
or, even better, run it in a docker container
with the exposed folder mounted inside.


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

