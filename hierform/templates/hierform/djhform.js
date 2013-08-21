YUI().use(['node', 'io-form'], function (Y) {
    var formid = '{{ formid }}';
    var ajaxurl = '{{ ajaxurl }}';
    function handleSelect(e) {
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
                            Y.one("#"+n.get('id')).replace(n);
                        }
                    }
                    nodelist.each(findAndReplace);
                },
                failure: function (id, result, args) { console.log("IO error"); }
            },
            arguments: null
        });
        try {
            e.currentTarget.ancestor('tr').next().one('select').set('innerHTML', '<option>Loading...</option>');
        } catch (ex) {} 
    }
    Y.one('#'+formid).delegate('change', handleSelect, '.djhselect');
});
