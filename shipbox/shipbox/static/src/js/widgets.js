odoo.define('shipbox.widgets', function (require) {
"use strict";

var basic_fields = require('web.basic_fields');
var registry = require('web.field_registry');

var FieldScale = basic_fields.InputField.extend({
    className: 'o_field_scale o_field_number',
    tagName: 'span',
    supportedFieldTypes: ['float'],

    /**
     * FieldScale
     *
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);

        if (this.mode === 'edit') {
            this.tagName = 'div';
            this.className += ' o_input';
        }

        this.formatOptions.digits = [16, 3];
        this.formatOptions.field_digits = this.nodeOptions.field_digits;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * For weight fields, 0 is a valid value.
     *
     * @override
     */
    isSet: function () {
        return this.value === 0 || this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * For weight fields, the input is inside a div, alongside a span
     * containing the current weight.
     *
     * @override
     * @private
     */
    _renderEdit: function () {
        this.$el.empty();

        // Prepare and add the input
        this._prepareInput().appendTo(this.$el);
        var $weight = $('<span>', {text: ' From Scale: ', class: 'btn btn-primary'}).append(
            $('<span>', {class: 'shipbox_scale_reading_auto'})
        );
        var handle = function(e) {
            e.preventDefault();
            var w = this.$el.find('.shipbox_scale_reading_auto').text();
            this.$el.find('input.o_input').val(w);
            this._setValue(w);
        };

        this.$el.append($weight);
        $weight.click(handle.bind(this));
    },
    /**
     * @override
     * @private
     */
    _renderReadonly: function () {
        this.$el.html(this._formatValue(this.value));
        var $weight = $('<span>', {text: ' From Scale: '}).append(
            $('<span>', {class: 'shipbox_scale_reading_auto'})
        );
        this.$el.append($weight);
    },
});


registry.add('scale', FieldScale);

return {
    FieldScale: FieldScale,
}

});
