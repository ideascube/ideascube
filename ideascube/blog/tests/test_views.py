from datetime import date, datetime

import pytest

from django.core.urlresolvers import reverse
from django.utils import translation, timezone

from ..views import Index
from ..models import Content
from .factories import ContentFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app):
    assert app.get(reverse('blog:index'), status=200)


def test_only_published_should_be_in_index_for_anonymous(
        app, published, draft, deleted, published_in_the_future):
    response = app.get(reverse('blog:index'))
    assert published.title in response.content.decode()
    assert draft.title not in response.content.decode()
    assert deleted.title not in response.content.decode()
    assert published_in_the_future.title not in response.content.decode()


def test_only_published_should_be_in_index_for_users(
        loggedapp, published, draft, deleted, published_in_the_future):
    response = loggedapp.get(reverse('blog:index'))
    assert published.title in response.content.decode()
    assert draft.title not in response.content.decode()
    assert deleted.title not in response.content.decode()
    assert published_in_the_future.title not in response.content.decode()


def test_published_and_drafts_and_future_should_be_in_index_for_staff(
        staffapp, published, draft, deleted, published_in_the_future):
    response = staffapp.get(reverse('blog:index'))
    assert published.title in response.content.decode()
    assert draft.title in response.content.decode()
    assert deleted.title not in response.content.decode()
    assert published_in_the_future.title in response.content.decode()


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    ContentFactory.create_batch(size=4, status=Content.PUBLISHED)
    response = app.get(reverse('blog:index'))
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(reverse('blog:index') + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(reverse('blog:index') + '?page=3', status=404)


def test_content_are_ordered_by_last_published_by_default(app):
    content3 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 15))
    content1 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 17))
    content2 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 16))
    response = app.get(reverse('blog:index'))
    titles = response.pyquery.find('.card.blog h3')
    assert titles[0].text == content1.title
    assert titles[1].text == content2.title
    assert titles[2].text == content3.title


def test_should_take_sort_parameter_into_account(app):
    content3 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 15))
    content1 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 17))
    content2 = ContentFactory(status=Content.PUBLISHED,
                              published_at=datetime(2016, 6, 26, 16, 16))
    response = app.get(reverse('blog:index'), params={'sort': 'asc'})
    titles = response.pyquery.find('.card.blog h3')
    assert titles[0].text == content3.title
    assert titles[1].text == content2.title
    assert titles[2].text == content1.title


def test_everyone_should_access_published_content(app, published):
    assert app.get(reverse('blog:content_detail',
                           kwargs={'pk': published.pk}), status=200)


def test_anonymous_should_not_access_draft_content(app, draft):
    assert app.get(reverse('blog:content_detail', kwargs={'pk': draft.pk}),
                   status=404)


def test_non_staff_should_not_access_draft_content(loggedapp, draft):
    assert loggedapp.get(reverse('blog:content_detail',
                                 kwargs={'pk': draft.pk}), status=404)


def test_staff_should_access_draft_content(staffapp, draft):
    assert staffapp.get(reverse('blog:content_detail',
                                kwargs={'pk': draft.pk}), status=200)


def test_anonymous_should_not_access_published_in_the_future_content(
        app,
        published_in_the_future):
    assert app.get(
        reverse('blog:content_detail',
                kwargs={'pk': published_in_the_future.pk}), status=404)


def test_non_staff_should_not_access_published_in_the_future_content(
        loggedapp,
        published_in_the_future):
    assert loggedapp.get(
        reverse('blog:content_detail',
                kwargs={'pk': published_in_the_future.pk}), status=404)


def test_staff_should_access_published_in_the_future_content(
        staffapp,
        published_in_the_future):
    assert staffapp.get(
        reverse('blog:content_detail',
                kwargs={'pk': published_in_the_future.pk}), status=200)


def test_anonymous_should_not_access_deleted_page(app, deleted):
    assert app.get(reverse('blog:content_detail', kwargs={'pk': deleted.pk}),
                   status=404)


def test_non_staff_should_not_access_delete_page(loggedapp, deleted):
    assert loggedapp.get(reverse('blog:content_detail',
                                 kwargs={'pk': deleted.pk}), status=404)


def test_staff_should_access_deleted_content(staffapp, deleted):
    assert staffapp.get(reverse('blog:content_detail',
                                kwargs={'pk': deleted.pk}), status=200)


def test_anonymous_should_not_access_edit_page(app, published):
    assert app.get(reverse('blog:content_update',
                           kwargs={'pk': published.pk}), status=302)


def test_non_staff_should_not_access_edit_page(loggedapp, published):
    assert loggedapp.get(reverse('blog:content_update',
                                 kwargs={'pk': published.pk}), status=302)


def test_staff_should_access_published_edit_page(staffapp, published):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': published.pk}), status=200)


def test_staff_should_access_draft_edit_page(staffapp, draft):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': draft.pk}), status=200)


def test_staff_should_access_deleted_edit_page(staffapp, deleted):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': deleted.pk}), status=200)


def test_staff_can_edit_published_content(staffapp, published):
    url = reverse('blog:content_update', kwargs={'pk': published.pk})
    form = staffapp.get(url).forms['model_form']
    title = "New title"
    assert Content.objects.get(pk=published.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=published.pk).title == title


def test_staff_can_edit_draft_content(staffapp, draft):
    url = reverse('blog:content_update', kwargs={'pk': draft.pk})
    form = staffapp.get(url).forms['model_form']
    title = "New title"
    assert Content.objects.get(pk=draft.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=draft.pk).title == title


def test_staff_can_edit_deleted_content(staffapp, deleted):
    url = reverse('blog:content_update', kwargs={'pk': deleted.pk})
    form = staffapp.get(url).forms['model_form']
    title = "New title"
    assert Content.objects.get(pk=deleted.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=deleted.pk).title == title


def test_published_at_is_YMD_formatted_even_in_other_locale(staffapp,
                                                            published):
    published.published_at = date(2015, 1, 7)
    published.save()
    translation.activate('fr')
    url = reverse('blog:content_update', kwargs={'pk': published.pk})
    form = staffapp.get(url).forms['model_form']
    assert form['published_at'].value == '2015-01-07'
    translation.deactivate()


def test_published_at_can_be_still_set_the_French_way(staffapp, published):
    # We force the input at load time, but we should still accept other format
    # at save.
    translation.activate('fr')
    url = reverse('blog:content_update', kwargs={'pk': published.pk})
    form = staffapp.get(url).forms['model_form']
    form['published_at'] = '11/01/2015'
    form.submit().follow()
    assert Content.objects.count()
    assert Content.objects.first().published_at.date() == date(2015, 1, 11)
    translation.deactivate()


def test_can_create_content_without_image(staffapp):
    assert not Content.objects.count()
    form = staffapp.get(reverse('blog:content_create')).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary'
    form['text'] = 'my content text'
    form['published_at'] = '2014-12-10'
    form.submit().follow()
    assert Content.objects.count()

def test_content_text_is_not_cleaned_from_wanted_html_tags(staffapp):
    form = staffapp.get(reverse('blog:content_create')).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary'
    form['text'] = ('<h2>A title</h2>'
                    '<p>Some text <a href="exemple.com">A link</a></p>')
    form['published_at'] = '2014-12-10'
    form.submit().follow()
    content = Content.objects.first()
    assert content.text == ('<h2>A title</h2>'
                            '<p>Some text <a href="exemple.com">A link</a></p>')


def test_content_text_is_cleaned_from_unwanted_html_tags(staffapp):
    form = staffapp.get(reverse('blog:content_create')).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary'
    form['text'] = ('</div><script type="text/javascript">'
                    'alert("boo");</script><div><p>'
                    '<a href="exemple.com">A link</a></p><')
    form['published_at'] = '2014-12-10'
    form.submit().follow()
    content = Content.objects.first()
    assert content.text == ('&lt;script type="text/javascript"&gt;'
                            'alert("boo");&lt;/script&gt;&lt;div&gt;<p>'
                            '<a href="exemple.com">A link</a></p>'
                            '&lt;&lt;/div&gt;')


def test_content_summary_is_cleaned_from_unwanted_html_tags(staffapp):
    form = staffapp.get(reverse('blog:content_create')).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary <img src="foo" />'
    form['text'] = ('my content text')
    form['published_at'] = '2014-12-10'
    form.submit().follow()
    content = Content.objects.first()
    assert content.summary == ('my content summary &lt;img src="foo"&gt;')


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = ContentFactory(status=Content.PUBLISHED, tags=['plane'])
    boat = ContentFactory(status=Content.PUBLISHED, tags=['boat'])
    response = app.get(reverse('blog:index'), params={'tags': 'plane'})
    assert plane.title in response.content.decode()
    assert boat.title not in response.content.decode()


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    ContentFactory.create_batch(size=4, status=Content.PUBLISHED,
                                tags=['plane'])
    url = reverse('blog:index')
    response = app.get(url, params={'tags': 'plane'})
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url, params={'tags': 'plane', 'page': 2})
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url, params={'tags': 'plane', 'page': 3}, status=404)


def test_can_create_content_with_tags(staffapp):
    url = reverse('blog:content_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary'
    form['text'] = 'my content text'
    form['published_at'] = '2014-12-10'
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    content = Content.objects.last()
    assert content.tags.count() == 2
    assert content.tags.first().name == 'tag1'


def test_can_update_content_tags(staffapp, published):
    assert published.tags.count() == 0
    url = reverse('blog:content_update', kwargs={'pk': published.pk})
    form = staffapp.get(url).forms['model_form']
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    content = Content.objects.get(pk=published.pk)
    assert content.tags.count() == 2
    assert content.tags.first().name == 'tag1'


def test_staff_user_cannot_delete_user_linked_to_blog_content(staffapp,
                                                              published):
    assert len(Content.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': published.author.pk})
    form = staffapp.get(url).forms['delete_form']
    resp = form.submit()
    assert resp.status_code == 302
    assert resp['Location'].endswith(published.author.get_absolute_url())
    assert len(Content.objects.all()) == 1


def test_text_is_kept_on_invalid_form(staffapp, published):
    url = reverse('blog:content_update', kwargs={'pk': published.pk})
    form = staffapp.get(url).forms['model_form']
    text = "this is my new text"
    form['text'] = text
    form['summary'] = ''  # Make form invalid.
    response = form.submit()
    assert response.pyquery.find('div[id="text"]').text() == text


def test_create_content_with_default_values(staffapp):
    assert not Content.objects.count()
    form = staffapp.get(reverse('blog:content_create')).forms['model_form']
    form['title'] = 'my content title'
    form['summary'] = 'my content summary'
    form['text'] = 'my content text'
    form.submit().follow()
    content = Content.objects.last()
    assert content.author == staffapp.user
    assert content.published_at.date() == timezone.now().date()
