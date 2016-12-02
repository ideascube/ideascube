

import yaml
import os.path as op
import zipfile
import codecs
import csv


class MediaCenterPackage:
    def __init__(self, working_dir, medias=None, report=None):
        self.working_dir = working_dir
        self.medias = []
        for line, media in enumerate(medias or [], 1):
            if self.check_media(line, media, report):
                self.medias.append(media)

    def check_media(self, line, media, report):
        for required_metadata in ('title', 'summary', 'credits', 'path'):
            if not media.get(required_metadata):
                if report:
                    report.warning("Metadata missing, ignoring the"
                                   " corresponding media",
                                   "{} at line {}"
                                   .format(required_metadata, line))
                return False
        full_path = op.join(self.working_dir, media['path'])
        if not op.exists(full_path):
            if report:
                report.warning("Path does not exist, ignoring the"
                               " corresponding media",
                               "{} used at line {}".format(full_path, line))
            return False
        preview_path = media.get('preview')
        if (preview_path
           and not op.exists(op.join(self.working_dir, preview_path))):
            if report:
                report.warning("Preview path does not exist.",
                               "{} used at line {}".format(preview_path, line))
            media['preview'] = None
        return True

    @classmethod
    def from_csv(cls, csv_path, report=None):
        working_dir = op.dirname(csv_path)
        with codecs.open(csv_path, 'r') as f:
            content = f.read()
            try:
                dialect = csv.Sniffer().sniff(content)
            except csv.Error:
                dialect = csv.unix_dialect()
            medias = list(csv.DictReader(content.splitlines(), dialect=dialect))
            return cls(working_dir, medias, report)

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
