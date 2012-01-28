YUI().use(['node', 'io-form'], function (Y) {
    var formid = '{{ formid }}';
    var ajaxurl = '{{ ajaxurl }}';
    function handleSelect() {
        Y.io(ajaxurl, {
            method: 'GET',
            form: { id : formid },
            on: {
                success: function (id, result, args) { 
                    var nodelist = Y.Node.create(result.responseText).get('childNodes');
                    function findAndReplace(newnode) {
                        var n = newnode.one('select');
                        if(n)
                        {
                            Y.one("#"+n.get('id')).setContent(n.get('childNodes'));
                        }
                    }
                    nodelist.each(findAndReplace);
                },
                failure: function (id, result, args) { console.log("IO error"); }
            },
            arguments: null
        });
    }
    Y.one('#'+formid).delegate('change', handleSelect, 'select');
});
