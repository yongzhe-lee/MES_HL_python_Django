(function ($, kendo) {
    let ui = kendo.ui,
        Form = ui.Form;

    let CustomForm = Form.extend({
        init: function (element, options) {
            Form.fn.init.call(this, element, options);
            this._makeSameCss(options);
        },

        options: {
            name: "CustomForm"
        },

        getData: function (field) {
            let items = this.options.items;
            let formElement = this.element;
            let data = {};
            let field_value = '';

            try {
                items.forEach(function (item) {
                    let editorSelector = "[name='" + (item.attributes && item.attributes.name || item.field) + "']";
                    let $editor = formElement.find(editorSelector);
                    let editor = item.editor;
                    let currentValue = '';

                    // 커스텀은 아직 고려 안 함
                    if (editor == 'ComboBox') {
                        let combobox = $editor.data('kendoComboBox');
                        currentValue = combobox.value();
                    } else if (editor == 'TextBox') {
                        let textbox = $editor.data('kendoTextBox');
                        currentValue = textbox.value();
                    } else if (editor == 'Switch') {
                        let switchButton = $editor.data('kendoSwitch');
                        currentValue = switchButton.value() == true ? 'Y' : 'N';
                    } else if (editor == 'TextArea') {
                        let textarea = $editor.data('kendoTextArea');
                        currentValue = textarea.value();
                    } else if (editor == 'NumericTextBox') {
                        let numericTextBox = $editor.data('kendoNumericTextBox');
                        currentValue = numericTextBox.value();
                    } else if (editor == 'hidden') {
                        currentValue = $editor.val();
                    }

                    if (field && field == item.field) {
                        field_value = currentValue;
                        throw new Error();
                    }

                    data[item.field] = currentValue;
                });
            } catch (e) {
                if (field) {
                    return field_value
                }
            }

            return data;
        },

        setData: function (data) {
            let items = this.options.items;
            let formElement = this.element;
            items.forEach(function (item) {
                let editorSelector = "[name='" + (item.attributes && item.attributes.name || item.field) + "']";
                let $editor = formElement.find(editorSelector);
                let editor = item.editor;
                let currentValue = data[item.field];

                if (currentValue === undefined) {
                    return;
                }

                // 커스텀은 아직 고려 안 함
                if (editor == 'ComboBox') {
                    let combobox = $editor.data('kendoComboBox');
                    combobox.value(currentValue);
                } else if (editor == 'TextBox') {
                    let textbox = $editor.data('kendoTextBox');
                    textbox.value(currentValue);
                } else if (editor == 'Switch') {
                    let switchButton = $editor.data('kendoSwitch');
                    switchButton.check(currentValue == 'Y' ? true : false);
                } else if (editor == 'TextArea') {
                    let textarea = $editor.data('kendoTextArea');
                    textarea.value(currentValue);
                } else if (editor == 'NumericTextBox') {
                    let numericTextBox = $editor.data('kendoNumericTextBox');
                    numericTextBox.value(currentValue);
                } else if (editor == 'hidden') {
                    $editor.val(currentValue);
                }
            });
        },

        _makeSameCss: function (options) {
            let formElement = this.element;
            let cssMarginTopValue = 'var(--kendo-spacing-3\\.5, 0.875rem)';

            let marginElement1 = formElement.find('.k-form-field');
            let marginElement2 = formElement.find('.k-form-buttons');

            marginElement1.css('margin-top', cssMarginTopValue);
            marginElement2.css('margin-top', cssMarginTopValue);
        },

        // type이 hidden인 경우 clear시 값이 남아 있으므로 재정의
        clear: function () {
            Form.fn.clear.call(this);
            let items = this.options.items;
            let formElement = this.element;

            items.forEach(function (item) {
                if (item.editor === "hidden") {
                    var editorSelector = "[name='" + (item.attributes && item.attributes.name || item.field) + "']";
                    formElement.find(editorSelector).val('');
                }
            });
        }
    });

    ui.plugin(CustomForm);
})(jQuery, kendo);

