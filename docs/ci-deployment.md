# Ideascube CI deployment

We have a CI system deployed for the Ideascube project.

It uses [Buildbot](https://buildbot.net) to pilot
[sbuild](https://wiki.debian.org/sbuild) builds of Debian packages.

There are two types of machines that were deployed:

* A single **master**, piloting the work to be done
* Multiple **workers**, actually doing the work

The rest of this documentation is structured in a way that reflects this.

**Note:** When following this documentation, you must replace the following
variables:

* `$arch` by the architecture of the worker you are deploying, for example
    `amd64` or `armhf`

## Deploying a worker machine

We currently have only one worker machine:

* an `amd64` machine (which also runs the master)

**TODO:** Deploy an `armhf` worker.

### Pre-requisites

A few things need to be installed before we start:

```
# apt install sbuild dh-virtualenv git
```

It is also necessary to create a new user which will run Buildbot:

```
# useradd -c "Buildbot user" -d /srv/buildbot -m -s /bin/bash buildbot
# passwd buildbot
```

This user will also need to be a sudoer for certain commands, so add the
following lines with the `visudo` command:

```
# Allow buildbot to update the sbuild chroots without a password
buildbot  ALL=(root) NOPASSWD: /usr/bin/sbuild-update
```

Finally, there are a couple of directories to create:

```
# mkdir /srv/chroot{,-tarballs}
# chown root:sbuild /srv/chroot{,-tarballs}
# chmod g+w /srv/chroot{,-tarballs}
```

### Configuring sbuild

We want to be able to build Debian packages properly, in an unattended and
reproducible way.

The Debian developers use sbuild to do that, so it seems like a good idea to
do the same.

A few things are needed in order to get a working sbuild deployment:

```
# sbuild-update --keygen
# sbuild-adduser buildbot
# sbuild-createchroot \
    --make-sbuild-tarball=/srv/chroot-tarballs/jessie-$arch.tar.gz \
    --arch=$arch \
    jessie \
    /srv/chroot/jessie-$arch \
    http://httpredir.debian.org/debian
```

At this point, you should have a functional `sbuild`. You could test it by
running the following commands as the `buildbot` user:

```
$ sudo sbuild-update -udcar jessie-$arch-sbuild
$ git clone https://github.com/ideascube/ideascube
$ cd ideascube
$ sbuild -s -d jessie --arch $arch
```

If the `sbuild` command finished successfully, you'll find an
`ideascube-VERSION.deb` package in the parent directory of your Ideascube git
tree. You can remove the git tree as well as the build artefacts, they are not
necessary any more.

### Deploying the Buildbot worker

Unfortunately, the Debian packages for buildbot are too old, so we will use
the latest version (as of this writing, it is version 0.8.12) in a virtual
environment.

As the `buildbot` user, run the following commands to install the Buildbot
worker code:

```
$ virtualenv venv
$ . ./venv/bin/activate
$ pip install "buildbot-slave==0.8.12"
```

Next, create the worker:

```
$ buildslave create-slave -r slave-$arch $master_host:master_port slave-$arch $password
```

In the above command, some variables are important to explain:

* `$master_host` is the host name or IP address of the machine where the
    Buildbot master runs (or will run). It could be `localhost` if the worker
    being created runs on the same machine as the master.
* `master_port` is the private protocol port of the Buildbot master. By
    default this is `9989`, but it can be changed when configuring the master
    (see below)
* `password` is the password for this worker to authenticate with the master.
    Remember it, you will need to specify it in the master's configuration.

Next, edit the `slave-$arch/info/admin` and `slave-$arch/info/host` files.

Create the `/etc/systemd/system/buildbot-worker@.service` file:

```
[Unit]
Description=The Buildbot Worker for the %I architecture

[Service]
User=buildbot
ExecStart=/srv/buildbot/venv/bin/buildslave start --nodaemon /srv/buildbot/slave-%I

[Install]
WantedBy=multi-user.target
```

Then, start and enable the new worker service:

```
# systemctl daemon-reload
# systemctl start buildbot-worker@$arch.service
# systemctl enable buildbot-worker@$arch.service
# systemctl status buildbot-worker@$arch.service
```

At this point, your worker is ready to accept tasks.

## Deploying the master machine

At the moment, our master runs on the same machine as our amd64 worker.

### Pre-requisites

**Note:** If your master runs on the same machine as an already configured
worker, you can skip the user creation step as you have already done it when
deploying the worker.

It is necessary to create a new user which will run Buildbot:

```
# useradd -c "Buildbot user" -d /srv/buildbot -m -s /bin/bash buildbot
# passwd buildbot
```

### Deploying the Buildbot master

Unfortunately, the Debian packages for buildbot are too old, so we will use
the latest version (as of this writing, it is version 0.8.12) in a virtual
environment.

**Note:** If your master runs on the same machine as an already configured
worker, you should already have a virtual environment ready.

As the `buildbot` user, run the following commands to install the Buildbot
master code:

```
$ virtualenv venv
$ . ./venv/bin/activate
$ pip install "buildbot==0.8.12"
```

Next, create the master:

```
$ buildbot create-master -r master
```

Create the `master/master.cfg` file, the open it with your favourite text
editor:

```
$ cp master/master.cfg.sample master/master.cfg
$ vim master/master.cfg
```

In this file, there are a few things you will need to configure. The file
already contains something for all of these, as examples, so you can just
search for the keys, and replace the values.

First, configure the project identity:

```
c['title'] = 'Ideascube'
c['titleURL'] = 'https://github.com/ideascube'
c['buildbotURL'] = 'http://buildbot.ideas-box.fr/'                             # TODO
```

Next, let the master know about the worker(s):

```
c['slaves'] = [
    buildslave.BuildSlave('slave-$arch', '$password'),
    ]
```

You must add one `buildslave.BuildSlave(...)` line for **each** worker you
have already deployed. If you deploy new workers in the future, they will need
to be added here before they can be used.

Do **not** use the `$arch` and `$password` variables in the configuration
file, you **must** replace them by their actual values.

In the above configuration snippet, `$password` is the password you supplied
when creating the worker. It will let the master authenticate the worker.

One more thing about the workers, the default `master.cfg` file contains this
snippet:

```
c['protocols'] = {'pb': {'port': 9989}}
```

This is the private protocol port of the Buildbot master, to which the
Buildbot workers will connect. It **must** correspond to the `master_port`
value you used (or will use) when creating workers. (see the worker
deployment documentation) Feel free to leave this line to its default value.
Make sure the workers can access the master on this port, though. (open the
firewall if necessary)

The default master configuration file also contains a "change source", which
will regularly poll for changes in the Git repository. Since we will not poll,
but instead rely on web hooks from Github, you can just remove all change
sources:

```
c['change_source'] = []
```

Now, configure the task scheduling. We will add two schedulers:

* one to be able to force tasks manually, whenever we want,
* one to act automatically when new tags were created in the Ideascube git
    repository.

You can remove what is in the default `master.cfg` and replace it by this
configuration snippet:

```
c['schedulers'] = [
    schedulers.ForceScheduler(
        name='force',
        builderNames=[
            'build-$arch-pkg',
            ]),
    schedulers.AnyBranchScheduler(
        name='tags',
        categories=['new-tag'],
        builderNames=[
            'build-$arch-pkg',
            ]),
    ]
```

Again, in the snippet above, do **not** use the `arch` variable, but instead
replace it by its actual value. In addition, be sure to add one line for each
worker in both of the `builderNames` lists.

Next, configure the task builders:

```
$arch_pkg_factory = util.BuildFactory()
$arch_pkg_factory.addStep(steps.Git(
    repourl='git://github.com/ideascube/ideascube.git',
    mode='incremental', branch='master'))
$arch_pkg_factory.addStep(steps.ShellCommand(
    command=['sudo', 'sbuild-update', '-udcar', 'jessie-$arch-sbuild']))
$arch_pkg_factory.addStep(steps.ShellCommand(
    command=['sbuild', '-s', '-d', 'jessie', '--arch', '$arch']))

c['builders'] = [
    util.BuilderConfig(
        name='build-$arch-pkg', slavenames=['slave-$arch'],
        factory=$arch_pkg_factory),
    ]
```

As is becoming usual, do not use the `$arch` variable in the snippet above,
but be sure to replace it by its actual value. That means you will need to add
one factory and one builder for each Buildbot worker.

Finally, configure the Buildbot web application. It allows a few things:

* it reports the status of tasks
* it allows forcing a task manually
* it provides a web hook that Github can call to report events

```
from datetime import datetime
from buildbot.status import html, web
from buildbot.status.web.hooks.github import GitHubEventHandler

class GithubCreateEventHandler(GitHubEventHandler):
    def handle_create(self, payload):
        ref_name = payload['ref']
        ref_type = payload['ref_type']

        if ref_type != 'tag':
            # Ignore, we are only interested in new tags
            return [], 'git'

        change = {
            'revision': ref_name,
            'when_timestamp': datetime.now(),
            'branch': ref_name,
            'repository': payload['repository']['clone_url'],
            'category': 'new-tag',
            'author': payload['sender']['login'],
            'comments': 'Tag %s created' % ref_name,
            'project': payload['repository']['full_name']
        }

        return [change], 'git'

authz_cfg = web.authz.Authz(
    auth=web.auth.BasicAuth([('$admin_login', '$admin_password')]), forceBuild='auth',
    forceAllBuilds='auth', gracefulShutdown=False, pingBuilder=False,
    stopBuild=False, stopAllBuilds=False, cancelPendingBuild=False)

c['status'] = [
    html.WebStatus(
        http_port=8010, authz=authz_cfg,
        change_hook_dialects={
            'github': {
                'class': GithubCreateEventHandler,
                'secret': '$secret',
                'strict': False,
                },
            },
        ),
    ]
```

(Yes, having the code for that `GithubCreateEventHandler` class directly in
the configuration file is pretty ugly. Hopefully, a future version of Buildbot
would ship an improved Github event handler so that we could drop ours)

Of course, in the above snippet, replace the `$admin_login` and
`$admin_password` variables by their actual values. They are used to
authenticate on the Buildbot web application, which is required to manually
for tasks.

In the same way, the `$secret` variable should be replaced by the secret value
given to Github when configuring the web hook.

At this point your Buildbot master should be fully configured, so you can
close the `master.cfg` file.

Create the `/etc/systemd/system/buildbot-master.service` file:

```
[Unit]
Description=The Buildbot Master

[Service]
User=buildbot
ExecStart=/srv/buildbot/venv/bin/buildbot start --nodaemon /srv/buildbot/master

[Install]
WantedBy=multi-user.target
```

Then, start and enable the new master service:

```
# systemctl daemon-reload
# systemctl start buildbot-master.service
# systemctl enable buildbot-master.service
# systemctl status buildbot-master.service
```

At this point, your master is fully operational, ready to dispatch tasks to
the worker(s).
