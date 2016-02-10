import yaml


class InvalidFile(Exception):
    pass


class Remote:
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            d = yaml.safe_load(f.read())

            try:
                return cls(d['id'], d['name'], d['url'])

            except KeyError as e:
                raise InvalidFile(
                    'Remote file is missing a {} key: {}'.format(e, path))

    def to_file(self, path):
        with open(path, 'w') as f:
            d = {'id': self.id, 'name': self.name, 'url': self.url}
            f.write(yaml.safe_dump(d, default_flow_style=False))
