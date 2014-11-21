# ideasbox.lan

This Django repository is the main application of the Ideas Box server.

More details about the server of the [overview](https://github.com/ideas-box/ideasbox.lan/wiki/Server-Overview)

## Custom user model
When setting up an Ideas Box server, if you need custom properties on the user
model, you should create a new model that inherits from
`ideasbox.models.DefaultUser`, and to have Django use it, you need to
set the environment variable `AUTH_USER_MODEL` **before running the initial
Django migration**.

## IRC

`#ideasbox` on `irc.freenode.net`
