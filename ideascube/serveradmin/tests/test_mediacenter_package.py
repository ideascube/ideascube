import zipfile
import yaml
import os

from ..package import MediaCenterPackage

import pytest

from ideascube.mediacenter.models import Document


def test_create_a_package_from_csv(csv_writer):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,my image,my image summary,BSF,an-image.jpg\n')
    csv_path = csv_writer(metadata)
    package = MediaCenterPackage.from_csv(csv_path)
    assert len(package.medias) == 3
    assert package.medias == [{'title': 'my video',
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
                               'path': 'an-image.jpg'
                              }
                             ]


@pytest.mark.parametrize('metadata', [
    ('kind,title,summary,credits,path,preview\n'
     'video,my video,my video summary,BSF,a-video.mp4,'),
    ('kind,title,summary,credits,path,preview\n'
     'video,my video,my video summary,BSF,a-video.mp4,NOT_EXIST'),
    ('kind,title,summary,credits,path\n'
     'video,my video,my video summary,BSF,a-video.mp4')
])
def test_no_preview_in_csv(csv_writer, metadata):
    csv_path = csv_writer(metadata)
    package = MediaCenterPackage.from_csv(csv_path)
    assert not package.medias[0].get('preview')


def test_preview_in_csv(csv_writer):
    metadata = ('kind,title,summary,credits,path,preview\n'
                'video,my video,my video summary,BSF,a-video.mp4,an-image.jpg')
    csv_path = csv_writer(metadata)
    package = MediaCenterPackage.from_csv(csv_path)
    assert package.medias[0]['preview'] == 'an-image.jpg'


@pytest.mark.parametrize('row', [
    'image,,my summary,BSF,an-image.jpg',
    'image,my title,,BSF,an-image.jpg',
    'image,my title,my summary,,an-image.jpg',
    'image,my title,my summary,BSF,',
    'image,my title,my summary,BSF,unknownpath.mp4',
])
def test_should_skip_if_missing_required_metadata(
        package_path, csv_writer, row):
    metadata = ('kind,title,summary,credits,path\n' + row)
    csv_path = csv_writer(metadata)
    package = MediaCenterPackage.from_csv(csv_path)
    assert not package.medias


def test_create_zip_package(package_path):
    package = MediaCenterPackage(
                  os.path.join(os.path.dirname(__file__), 'data'),
                  medias=[{'title': 'my video',
                           'summary': 'my video summary',
                           'kind': 'video',
                           'credits': 'BSF',
                           'path': 'a-video.mp4',
                           'preview': 'an-image1.jpg'},
                          {'title': 'my doc',
                           'summary': 'my doc summary',
                           'kind': 'pdf',
                           'credits': 'BSF',
                           'path': 'a-pdf.pdf',
                           'preview': 'an-image.jpg'},
                          {'title': 'my image',
                           'summary': 'my image summary',
                           'kind': 'image',
                           'credits': 'BSF',
                           'path': 'an-image.jpg'
                          }
                         ])
    package.create_package_zip(package_path)
    with zipfile.ZipFile(package_path) as package:
        assert set(package.namelist()) == set(['manifest.yml',
                                               'a-video.mp4',
                                               'a-pdf.pdf',
                                               'an-image.jpg',
                                               'an-image1.jpg'])
        with package.open('manifest.yml') as m:
            manifest = yaml.load(m)
        assert manifest == {'medias': [
                                {'title': 'my video',
                                 'summary': 'my video summary',
                                 'kind': 'video',
                                 'credits': 'BSF',
                                 'path': 'a-video.mp4',
                                 'preview': 'an-image1.jpg'},
                                {'title': 'my doc',
                                 'summary': 'my doc summary',
                                 'kind': 'pdf',
                                 'credits': 'BSF',
                                 'path': 'a-pdf.pdf',
                                 'preview': 'an-image.jpg'},
                                {'title': 'my image',
                                 'summary': 'my image summary',
                                 'kind': 'image',
                                 'credits': 'BSF',
                                 'path': 'an-image.jpg'
                                }
                           ]}


@pytest.mark.usefixtures('db')
def test_created_zip_package_is_installable(package_path, tmpdir):
    from ideascube.serveradmin.catalog import ZippedMedias
    assert Document.objects.count() == 0

    package = MediaCenterPackage(
                  os.path.join(os.path.dirname(__file__), 'data'),
                  medias=[{'title': 'my video',
                           'summary': 'my video summary',
                           'kind': 'video',
                           'credits': 'BSF',
                           'path': 'a-video.mp4',
                           'preview': 'an-image1.jpg'},
                          {'title': 'my doc',
                           'summary': 'my doc summary',
                           'kind': 'pdf',
                           'credits': 'BSF',
                           'path': 'a-pdf.pdf',
                           'preview': ''},
                          {'title': 'my image',
                           'summary': 'my image summary',
                           'kind': 'image',
                           'credits': 'BSF',
                           'path': 'an-image.jpg'
                          }])
    package.create_package_zip(package_path)

    package2install = ZippedMedias('test-media',
                                  {'url': 'https://foo.fr/test-media.zip'})
    package2install.install(package_path, str(tmpdir))

    assert Document.objects.count() == 3
    video = Document.objects.get(title='my video')
    assert video.summary == 'my video summary'
    assert video.kind == Document.VIDEO
    assert os.path.basename(video.preview.name) == 'an-image1.jpg'
