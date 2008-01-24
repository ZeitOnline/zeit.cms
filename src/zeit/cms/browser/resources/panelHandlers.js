// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

function setCookie(name, value, expires, path, domain, secure) {   
  var val = escape(value);
  cookie = name + "=" + val +
    ((expires) ? "; expires=" + expires.toGMTString() : "") +
    ((path) ? "; path=" + path : "") +
    ((domain) ? "; domain=" + domain : "") +
    ((secure) ? "; secure" : "");
  document.cookie = cookie;
}

function getCookie(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  } else {
    begin += 2;
  }
  var end = document.cookie.indexOf(";", begin);
  if (end == -1) {
    end = dc.length;
  }
  return unescape(dc.substring(begin + prefix.length, end));
}

function PanelHandler(base_url) {
    this.url = base_url + '/panel_handlers';
}

PanelHandler.prototype = {

    registerPanelHandlers: function() {
        var panels = getElementsByTagAndClassName('div', 'panel');
        var handler = this;

        forEach(panels, function(panel) {
            var foldmarker = panel.getElementsByTagName('h1')[0];
            connect(foldmarker, "onclick", function(event) {
                if (event.target() != foldmarker) return;
                var new_state;
                if (hasElementClass(panel, 'folded')) {
                    removeElementClass(panel, 'folded');
                    addElementClass(panel, 'unfolded');
                } else {
                    removeElementClass(panel, 'unfolded');
                    addElementClass(panel, 'folded');
                }
                handler.storeState(panel.id);
            });
            var content_element = getFirstElementByTagAndClassName(
                'div', 'PanelContent', panel);
            var scroll_state = new ScrollStateRestorer(content_element);
            scroll_state.connectWindowHandlers();
        });

    },

    storeState: function(panel_id) {
        doSimpleXMLHttpRequest(this.url, {toggle_folding: panel_id});
    },


};



// Handler to close and open the sidebar making more space for the actual
// content area.

function SidebarDragger(base_url) {
    this.url = base_url + '/@@sidebar_toggle_folding';
    this.observe_ids = new Array('sidebar', 'sidebar-dragger', 
        'visualContentWrapper', 'visualContentWrapper', 'breadcrumbs');
}

SidebarDragger.prototype = {

    classes: ['sidebar-folded', 'sidebar-expanded'],
    
    toggle: function(event) {
        var dragger = this;
        var d = doSimpleXMLHttpRequest(this.url);
        d.addCallback(function(result) {
            var css_class = result.responseText;
            dragger.setClass(css_class);
        });
    },

    setClass: function(css_class) {
        var dragger = this;
        for (var i=0; )
        forEach(this.observe_ids,
            function(element_id) {
              forEach(dragger.classes, function(cls) {
                  var element = getElement(element_id);
                  removeElementClass(element, cls);
                  });
        addElementClass(element, css_class);
        });
    },
}


var ScrollStateRestorer = Class.extend({

    construct: function(content_element) {
        this.content_element = $(content_element);
    },

    connectWindowHandlers: function() {
        var othis = this;
        this.restoreScrollState();
        connect(window, 'onunload', function(event) {
            othis.rememberScrollState();
        });
        connect(this.content_element, 'initialload', function(event) {
            if (event.src() == othis.content_element) {
                othis.restoreScrollState();
            }
        });
    },

    rememberScrollState: function(content_element) {
        var position = this.content_element.scrollTop;
        var id = this.content_element.id;
        if (!id) {
            return;
        }
        setCookie(id, position.toString(), null, '/');
     },

    restoreScrollState: function() {
        var id = this.content_element.id;
        if (!id) {
            return;
        }
        var position = getCookie(id);
        this.content_element.scrollTop = position;
    },

});
