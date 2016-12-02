import zipfile
import yaml
import os
import pytest

from django.core.management import call_command


def test_csv2pkg_command(package_path, csv_writer, capsys):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,my image,my image summary,BSF,an-image.jpg\n')
    csv_path = csv_writer(metadata)
    call_command('csv2pkg', csv_path, package_path)
    out, err = capsys.readouterr()

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

    assert "Package {} has been created with 3 medias.".format(package_path) in out


def test_csv2pkg_wrong_metadata_command(package_path, csv_writer, capsys):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,,my image summary,BSF,an-image.jpg\n'
                'image,my image,,BSF,an-image.jpg\n'
                'image,my image,my image summary,,an-image.jpg\n'
                'image,my image,my image summary,BSF,\n'
                'image,my image,my image summary,BSF,an-image2.jpg\n')
    csv_path = csv_writer(metadata)
    call_command('csv2pkg', csv_path, package_path)
    out, err = capsys.readouterr()

    with zipfile.ZipFile(package_path) as package:
        assert set(package.namelist()) == set(['manifest.yml',
                                               'a-video.mp4',
                                               'a-pdf.pdf'])
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
                                        'path': 'a-pdf.pdf'}
                                      ]
                           }

    assert "Package {} has been created with 2 medias.".format(package_path) in out


def test_csv2pkg_wrong_metadata_verbose_command(package_path, csv_writer, capsys):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,,my image summary,BSF,an-image.jpg\n'
                'image,my image,,BSF,an-image.jpg\n'
                'image,my image,my image summary,,an-image.jpg\n'
                'image,my image,my image summary,BSF,\n'
                'image,my image,my image summary,BSF,an-image2.jpg\n')
    csv_path = csv_writer(metadata)
    call_command('csv2pkg', '--verbosity', '3', csv_path, package_path)
    out, err = capsys.readouterr()

    with zipfile.ZipFile(package_path) as package:
        assert set(package.namelist()) == set(['manifest.yml',
                                               'a-video.mp4',
                                               'a-pdf.pdf'])
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
                                        'path': 'a-pdf.pdf'}
                                      ]
                           }

    assert "title at line 3" in out
    assert "summary at line 4" in out
    assert "credits at line 5" in out
    assert "path at line 6" in out
    assert "data/an-image2.jpg used at line 7" in out

    assert "Package {} has been created with 2 medias.".format(package_path) in out


def test_csv2pkg_no_valid_media_verbose_command(package_path, csv_writer, capsys):
    metadata = ('kind,title,summary,credits,path\n'
                'image,,my image summary,BSF,an-image.jpg\n')
    csv_path = csv_writer(metadata)
    with pytest.raises(SystemExit):
        call_command('csv2pkg', '--verbosity', '3', csv_path, package_path)
    out, err = capsys.readouterr()

    assert "There is no (valid) media to create the package.".format(package_path) in err
    assert "title at line 1" in out
    assert not os.path.exists(package_path)


def test_csv2pkg_dry_run_do_not_create_package(package_path, csv_writer, capsys):
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,my image,my image summary,BSF,an-image.jpg\n')
    csv_path = csv_writer(metadata)
    call_command('csv2pkg', '--dry-run', csv_path, package_path)
    out, err = capsys.readouterr()
    assert "Package {} would have been created with 3 medias.".format(package_path) in out
    assert not os.path.exists(package_path)

