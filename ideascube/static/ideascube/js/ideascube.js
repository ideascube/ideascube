/*global document window Pikaday console gettext*/
/* eslint new-cap:0, strict:0, quotes:[2, "single"] global-strict:0, no-underscore-dangle:0, curly:0, consistent-return:0, no-new:0, no-console:0, space-before-function-paren:[2, "always"] */
'use strict';

ID.http = {

    _ajax: function (settings) {
        var xhr = new window.XMLHttpRequest();
        xhr.open(settings.verb, settings.uri, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                settings.callback.call(settings.context || xhr, xhr.status, xhr.responseText, xhr);
            }
        };
        xhr.send(settings.data);
        return xhr;
    },

    get: function (uri, options) {
        options.verb = 'GET';
        options.uri = uri;
        return ID.http._ajax(options);
    },

    queryString: function (params) {
        var queryString = [];
        for (var key in params) {
            queryString.push(encodeURIComponent(key) + '=' + encodeURIComponent(params[key]));
        }
        return queryString.join('&');
    }

};

ID.PROVIDERS = {
    '^(http(s)?://)?(www\.)?(youtube\.com|youtu\.be)': 'http://www.youtube.com/oembed',
    '^(http(s)?://)?(www\.)?dailymotion\.com': 'http://www.dailymotion.com/services/oembed',
    '^(https?://)?vimeo.com/': 'http://vimeo.com/api/oembed.json',
    '^(https?://)?(www\.)?flickr.com/': 'https://www.flickr.com/services/oembed/'
};

ID.matchProvider = function (value) {
    ID.PROVIDERS['^(https?://)?((www\.)?' + ID.DOMAIN + '/|localhost)'] = window.location.origin + window.location.pathname.slice(0, 3) + '/mediacenter/oembed/';
    for (var provider in ID.PROVIDERS) {
        if (value.match(provider)) return ID.PROVIDERS[provider];
    }
};

ID.image_url_resolver = function(data, resolve, reject) {
    var callback = function (status, resp) {
        if (status === 200) {
            try {
                resp = JSON.parse(resp);
            } catch (e) {
                reject({msg: ''});
                return;
            }
            if (resp.type === 'photo') {
                var img = document.createElement('IMG');
                img.setAttribute('src', resp.url);
                resolve({html: img.html});
            } else if (resp.type === 'video' || resp.type === 'rich') {
                resolve({html: resp.html});
            } else {
                reject({msg: 'Media type not supported'});
            }
        }
    };
    var providerUrl = ID.matchProvider(data.url);
    if (providerUrl) {
        var finalUrl = providerUrl + '?' + ID.http.queryString({url: data.url, format: 'json', maxwidth: '800'});
        var proxyUrl = '/ajax-proxy/?' + ID.http.queryString({url: finalUrl});
        ID.http.get(proxyUrl, {
            callback: callback
        });
    }
    else {
        reject({msg: 'Media provider not supported'});
    }
};


ID.initDatepicker = function (name) {
    new Pikaday({
        field: document.querySelector('[name="' + name + '"]'),
        format: 'YYYY-MM-DD',
        i18n: {
            previousMonth: gettext('Previous Month'),
            nextMonth: gettext('Next Month'),
            months: [gettext('January'), gettext('February'), gettext('March'), gettext('April'), gettext('May'), gettext('June'), gettext('July'), gettext('August'), gettext('September'), gettext('October'), gettext('November'), gettext('December')],
            weekdays: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
            weekdaysShort: [gettext('Sun'), gettext('Mon'), gettext('Tue'), gettext('Wed'), gettext('Thu'), gettext('Fri'), gettext('Sat')]
        }
    });
};

ID.focusOn = function (selector) {
    var element = document.querySelector(selector);
    if (element) element.focus();
};

ID.endswith = function (str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

ID.stopEnterKey = function (name) {
    var el = document.querySelector('[name="' + name + '"]');
    if (!el) return;
    var stop = function (e) {
        if (e.keyCode === 13) e.preventDefault();
    };
    el.addEventListener('keydown', stop, false);
};

ID.confirmClick = function (selector) {
    var el = document.querySelector(selector);
    if (!el) return;
    var ask = function (e) {
        if (!confirm(gettext('Are you sure?'))) {
            e.preventDefault();
            return false;
        }
    };
    el.addEventListener('click', ask, false);
};


ID.initWifiList = function (item_selector, popup_selector, urlroot) {
    var elements = document.querySelectorAll(item_selector);

    for (var i = 0; i < elements.length; ++i) {
        var element = elements[i];
        var known = element.getAttribute('data-known') === 'True';
        var secure = element.getAttribute('data-secure') === 'True';

        if (known || !secure) {
            var ssid = element.getAttribute('data-ssid');
            element.setAttribute('href', urlroot + ssid);
        } else {
            element.setAttribute('href', popup_selector);

            element.addEventListener('click', function (evt) {
                var ssid = this.getAttribute('data-ssid');
                var form = document.querySelector(popup_selector + ' form');
                form.setAttribute('action', urlroot + ssid);
            }.bind(element), true);
        }
    }
};


ID.viewablePassword = function () {
    var el = document.querySelector('input[type="password"]');
    if (!el) return;
    var wrapper = document.createElement('div'),
        button = document.createElement('i'),
        form = el.form;
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);
    el.className = el.className + ' showable-password';
    button.className = 'fa fa-eye show-password';
    wrapper.appendChild(button);
    var show = function (e) {
        el.type = 'text';
        window.setTimeout(hide, 1000);
    };
    var hide = function (e) {
        el.type = 'password';
    };
    button.addEventListener('click', show, false);
    form.addEventListener('submit', hide, false);
};

ID.initEditors = function () {
    var editors = document.querySelectorAll(".tinymce-editor");
    for (var i = 0; i < editors.length; i++) {
        var editor = editors[i];
        var use_media = editor.hasAttribute('tinymce_use_media');
        var options = {
            target : editor,
            inline: true,
            theme: "inlite",
            hidden_input: false,
            menubar: false,
            toolbar: false,
            selection_toolbar: "numlist bullist bold italic | quicklink h2 h3 blockquote",
            language: editor.getAttribute('tinymce_language_code'),
            media_url_resolver: ID.image_url_resolver,
            media_alt_source: false,
            media_poster: false,
            insert_toolbar: "numlist bullist bold italic | quicklink h2 h3 blockquote",
            contextmenu: "link",
            plugins: "autolink textpattern contextmenu lists"
        };
        if ( use_media )
        {
            options['insert_toolbar'] += " media";
            options['contextmenu'] += " media";
            options['plugins'] += " media";
        }
        tinymce.init(options);
   }
};
