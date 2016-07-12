import zipfile
import yaml

from django.core.management import call_command


def test_csv2package_command(package_path, csv_writer):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,my image,my image summary,BSF,an-image.jpg\n')
    csv_path = csv_writer(metadata)
    call_command('csv2package', csv_path, package_path)
    with zipfile.ZipFile(package_path) as package:
        assert set(package.namelist()) == set(['manifest.yml',
                                               'a-video.mp4',
                                               'a-pdf.pdf',
                                               'an-image.jpg'])
        with package.open('manifest.yml') as m:
            manifest = yaml.load(m)
        assert manifest == {'medias': [{'title': 'my video',
                                        'summary': 'my video summary',
                                        'kind': 'video',
                                        'credits': 'BSF',
                                        'path': 'a-video.mp4'},
                                       {'title': 'my doc',
                                        'summary': 'my doc summary',
                                        'kind': 'pdf',
                                        'credits': 'BSF',
                                        'path': 'a-pdf.pdf'},
                                       {'title': 'my image',
                                        'summary': 'my image summary',
                                        'kind': 'image',
                                        'credits': 'BSF',
                                        'path': 'an-image.jpg'}
                                      ]
                           }
