

import yaml
import os.path as op
import zipfile
import codecs
import csv


class MediaCenterPackage:
    def __init__(self, working_dir, medias=None):
        self.working_dir = working_dir
        self.medias = list(filter(self.check_media, medias or []))

    def check_media(self, media):
        for required_metadata in ('title', 'summary', 'credits', 'path'):
            if not media.get(required_metadata):
                return False
        if not op.exists(op.join(self.working_dir, media['path'])):
            return False
        preview_path = media.get('preview')
        if (preview_path
         and not op.exists(op.join(self.working_dir, preview_path))):
            print("Warning : preview_path {} defined but file does not exists"
                  .format(preview_path))
            media['preview'] = None
        return True

    @classmethod
    def from_csv(cls, csv_path):
        working_dir = op.dirname(csv_path)
        with codecs.open(csv_path, 'r') as f:
            content = f.read()
            try:
                dialect = csv.Sniffer().sniff(content)
            except csv.Error:
                dialect = csv.unix_dialect()
            medias = list(csv.DictReader(content.splitlines(), dialect=dialect))
            return cls(working_dir, medias)

    def create_package_zip(self, archive_path):
        with zipfile.ZipFile(archive_path,
                             mode='w',
                             allowZip64=True) as ziparchive:
            for mediaInfo in self.medias:
                filename = op.join(self.working_dir, mediaInfo['path'])
                ziparchive.write(filename=filename, arcname=mediaInfo['path'])
                preview_path = mediaInfo.get('preview')
                if preview_path:
                    preview_path = op.join(self.working_dir, preview_path)
                    ziparchive.write(filename=preview_path,
                                     arcname=mediaInfo['preview'])
            ziparchive.writestr('manifest.yml', self.dump_yaml())

    def dump_yaml(self):
        dump = {'medias': self.medias}
        return yaml.dump(dump, default_flow_style=None)
