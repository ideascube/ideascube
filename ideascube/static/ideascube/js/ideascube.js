/*global document window Pikaday console gettext*/
/* eslint new-cap:0, strict:0, quotes:[2, "single"] global-strict:0, no-underscore-dangle:0, curly:0, consistent-return:0, no-new:0, no-console:0, space-before-function-paren:[2, "always"] */
'use strict';

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
        var use_media = editor.hasAttribute('data-tinymce-use-media');
        var options = {
            target : editor,
            inline: true,
            theme: "inlite",
            hidden_input: false,
            menubar: false,
            toolbar: false,
            selection_toolbar: "numlist bullist bold italic | quicklink h1 h2 h3 blockquote",
            language: editor.getAttribute('data-tinymce-language-code'),
            relative_urls : false,
            insert_toolbar: "numlist bullist bold italic | quicklink h1 h2 h3 blockquote",
            contextmenu: "link",
            plugins: "autolink textpattern contextmenu lists"
        };
        if ( use_media )
        {
            options['insert_toolbar'] += " media_select";
            options['contextmenu'] += " media_select";
            options['plugins'] += " media mediacenter_select";
        }
        tinymce.init(options);
   }
};

ID.tinymce_insert_document = function (document_info) {
    var editor = top.tinymce.activeEditor;
    if (document_info.kind == 'image') {
        var element = document.createElement('img');
        element.setAttribute('src', document_info.original);
    } else if (document_info.kind == 'video' || document_info.kind == 'audio') {
        var element = document.createElement(document_info.kind);
        element.controls = true;
        element.preload  = 'none';
        element.innerHTML =
            gettext("Your web browser doesn't support this media type.");
        var source_element = document.createElement('source');
        source_element.src = document_info.original;
        element.appendChild(source_element);
    } else {
        var element = document.createElement('a');
        element.href = document_info.original;
        var img_element = document.createElement('img');
        if (document.preview) {
            img_element.src = document_info.preview;
        } else {
            img_element.src = document_info.icon;
        }
        element.appendChild(img_element);
    }
    editor.insertContent(element.outerHTML);
    editor.windowManager.close();
};
