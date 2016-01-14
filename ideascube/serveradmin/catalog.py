import yaml
import requests
import os


class Catalog(object):

    APP = 'app'
    CONTENT = 'content'
    TMP_DIR = '/tmp'

    def __init__(self):
        self.fetch()

    def fetch(self):
        with open('/home/ybon/Code/py/ideascube/ideascube/serveradmin/tests/data/catalog.yml') as f:
            self.source = yaml.load(f.read())
        self.apps = {}
        self.content = {}
        self.apps_by_mimetypes = {}
        for metadata in self.source['current']:
            if metadata['type'] == 'app':
                pass
            else:
                self.content[metadata['id']] = Content(metadata)

    def get_content(self, item):
        return self.content[item]

    def get_app(self, item):
        return self.apps[item]

    def install(self, id):
        package = self.get_content(id)
        app = Kiwix()
        app.install(package)


class Content(object):

    def __init__(self, metadata):
        self.__dict__.update(metadata)

    @property
    def download_path(self):
        return os.path.join(Catalog.TMP_DIR, self.id)

    def fetch(self):
        if not os.path.exists(self.download_path):
            # TODO: continue failed download
            # http://www.mobify.com/blog/http-requests-are-hard/ (on retrying)
            response = requests.get(self.url, stream=True)
            with open(self.download_path, mode='wb') as f:
                content = b''
                for count, chunk in enumerate(response.iter_content()):
                    content += chunk
                    if count % 1000 == 0:
                        f.write(content)
                        content = b''
                if content:
                    f.write(content)

    def install(self):
        self.fetch()


class Kiwix(object):

    DIR = '/tmp/kiwix'

    def install(self, package):
        package.fetch()
        pass
        # try:
        #     os.rename(package.download_path)
        # except OSError:
        #     pass
        # path = os.path.join(Catalog.TMP_DIR, package.id)
