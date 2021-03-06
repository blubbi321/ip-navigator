// -*- coding: utf-8 -*-
// (c) 2018 Andreas Motl <andreas.motl@ip-tools.org>
'use strict';

import { MarionetteFuture, DirectRenderMixin } from 'patzilla.lib.marionette';
import { CheckboxWidget } from 'patzilla.lib.hero-checkbox';

export { StackCheckboxWidget, StackOpenerWidget };


// TODO: Maybe
//const CheckboxBehavior = require('marionette-checkbox-behavior');


// TODO: Use https://github.com/rafeememon/marionette-checkbox-behavior
const StackCheckboxWidget = CheckboxWidget.extend({
    /*
    Contemporary <input type="checkbox"> elements with bidirectional data binding.
    Derived from https://github.com/rafeememon/marionette-checkbox-behavior
    */

    inputSelector: '> input',
    labelSelector: '> .text_label',

    // Forward the "click" dom event to a "toggle" application event
    triggers: {
        //'click': 'toggle',
    },

    initialize: function() {
        //log('StackCheckboxWidget::initialize');
        // https://makandracards.com/makandra/22121-how-to-call-overwritten-methods-of-parent-classes-in-backbone-js
        // https://stackoverflow.com/questions/15987490/backbone-view-inheritance-call-parent-leads-to-recursion/15988038#15988038
        StackCheckboxWidget.__super__.initialize.apply(this, arguments);
    },

});


const StackOpenerWidget = Backbone.Marionette.ItemView.extendEach(MarionetteFuture, DirectRenderMixin, {
    /*
    Button for opening the stack user interface
    also displaying the number of selected documents.

    It is a Material Design Component (MDC) button with dynamic content.
    */

    template: require('./stack-opener.html'),

    defaults: {
    },

    // Propagate model changes to user interface
    collectionEvents: {
        'sync': '_updateView',
    },

    ui: function() {
        return {
            count: '> #count',
        };
    },

    onRender: function() {
        //log('StackOpenerWidget::onRender');
        this._updateView();
    },

    get_selected_count: function() {
        var result = this.collection.where({selected: true});
        return result.length;
    },

    _updateView: function() {
        //log('StackOpenerWidget::_updateView');
        this.ui.count.html(this.get_selected_count());
    },

});
