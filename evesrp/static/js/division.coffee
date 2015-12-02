jQuery = require 'jquery'
require 'selectize'
ui = require './common-ui'
entityTableTemplate = require './templates/entity_table'
entityOptionTemplate = require './templates/entity_option'


render = (entities) ->
    for permission in ['submit', 'review', 'pay', 'audit', 'admin']
        $table = (jQuery "##{ permission }").find 'table'
        newTable = entityTableTemplate {
            entities: entities[permission]
            # This is not localized, as it's a programmatic identifier used in
            # a form.
            name: permission
        }
        $table.replaceWith newTable


selectAttribute = () ->
    $this = jQuery this
    attr = ($this.find 'option:selected').val()
    unless attr == ''
        ($this.find 'options[values=""]').remove()
    jQuery.ajax {
        type: 'GET'
        url: "#{ window.location.pathname }transformers/#{ attr }/"
        success: (data) ->
            $transformerSelect = jQuery 'select#transformer'
            $transformerSelect.empty()
            choices = data[attr]
            $transformerSelect.prop 'disabled', (choices.length == 1)
            for choice in choices
                $option = jQuery '<option></option>'
                $option.append choice[1]
                $option.attr 'value', choice[0]
                if choice[2] == true
                    $option.prop 'selected', true
                $transformerSelect.append $option
    }
    true


selectTransformer = () ->
    $this = jQuery this
    $form = $this.parents 'form'
    jQuery.ajax {
        type: 'POST'
        url: window.location.pathname
        data: $form.serialize()
    }
    true


changePermission = (ev) ->
    raise Exception


createEntitySelect = (selector) ->
    # Get opions first
    entitiesRequest = jQuery.ajax {
        type: 'GET'
        url: "#{ $SCRIPT_ROOT }/api/entities/"
    }
    entitiesRequest.done (data, textStatus, jqxhr) ->
        (jQuery selector).selectize {
            options: data.entities
            openOnFocus: false
            closeAfterSelect: true
            dropdownParent: 'body'
            searchField: ['name']
            # TODO Use the custom rendering functions to display auth source
            valueField: 'id'
            labelField: 'name'
            optgroups: {value: type} for type in ['User', 'Group']
            optgroupValueField: 'value'
            optgroupLabelField: 'value'
            optgroupField: 'type'
            onChange: (entityID) ->
                selectize = this
                $form = selectize.$input.closest 'form'
                $id = $form.find '#id_'
                $id.val entityID
                jQuery.ajax {
                    type: 'POST'
                    data: $form.serialize()
                    success: (data) ->
                        # Clear selection control now that this entity has been
                        # aded
                        selectize.clear(true)
                        $id.val ''
                    complete: (jqxhr) ->
                        data = jqxhr.responseJSON
                        render data.entities
                }
            render: {
                option: (item, escape) ->
                    entityOptionTemplate item
                optgroup_header: (data, escape) ->
                    # data will be either 'User' or 'Group' as specified in the
                    # various optgroup related options above.
                    i18n_value = ui.i18n.gettext data.value
                    "<div class=\"optgroup-header\"> #{ escape(i18n_value) }s</div>"
            }
        }


setupEvents = () ->
    (jQuery 'select#attribute').change selectAttribute
    (jQuery 'select#transformer').change selectTransformer
    createEntitySelect '.entity-typeahead'
    (jQuery '.permission').submit (ev) ->
        $form = (jQuery ev.target)
        jQuery.ajax {
            type: 'POST'
            url: window.location.pathname
            data: $form.serialize()
            complete: (jqxhr) ->
                data = jqxhr.responseJSON
                render data.entities
        }
        false

exports.setupEvents = setupEvents
