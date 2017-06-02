tinymce.PluginManager.add('mediacenter_select', function(editor, url) {
  // Add a button that opens a window
  editor.addButton('media_select', {
    icon: 'media',
    onclick: function() {
      // Open window
      editor.windowManager.open({
        // Nobreak space to be sure to have a space in the dialog header
        title: ' ',
        url: '/fr/mediacenter/select',
        width: 800,
        height: 600,
        buttons: [{
           text: 'Close',
           onclick: 'close'
        }]
      });
    }
  });
});

