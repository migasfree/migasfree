function change_data()
{
    if ($("#id_model").val() != "")
    {
        $.getJSON("/connections_model/?id=" + $("#id_model").val(), function(connection_list)
        {
            var html = '';
            for (var i = 0; i < connection_list.length; i++)
            {
                if (connection_list[i].pk == $("#id_connection").val())
                {
                    if (connection_list[i].fields['fields'] != '')
                    {
                        var fields = connection_list[i].fields['fields'].split(',');
                        var data = eval("("+ $("#id_data").val() + ")");
                        for (var j = 0; j < fields.length; j++)
                        {
                            html += '<div class="join">';
                            html += '<label for="join_' + fields[j] + '">' + fields[j] + '</label>';
                            html += '<input id="join_' + fields[j] + '" type="text" class="join_field" value="' + data[fields[j]] + '" />';
                            html += '</div>';

                        }
                    }
                }
            }

            //Remove Fields
            $('div.join').remove();

            // append new related fields
            $('div.field-data').append(html);
        });
    }
}


function change_model(default_value)
{
    default_value = default_value || '';

    if ($("#id_model").val() == '')
    {
        $("#id_connection").attr('disabled', true);
    }
    else
    {
        $.getJSON("/connections_model/?id="+$("#id_model").val(), function(j) {
            var options = '';
            for (var i = 0; i < j.length; i++) {
                options += '<option value="' + parseInt(j[i].pk) + '">' + j[i].fields['name'] + '</option>';
            }
            $("#id_connection").html(options);
            $("#id_connection").attr('disabled', false);

            if (default_value != '')
            {
                $('#id_connection option[value=' + default_value + ']').attr('selected', true);
            }
        });
        $("#id_model").attr('selected', 'selected');
        change_data();
    }
}


$(function() {
    // sólo se tiene que aplicar al formulario de entrada de datos
    if ($('#device_form').length) {
        $("#id_data").closest("div").hide();
        $("#id_data").attr("hidden", "hidden");

        if ($("#id_model").val() == '')
        {
            $("#id_connection").attr('disabled', true);
        }

        change_model($("#id_connection").val());

        $("#id_model").change(change_model);
        $("#id_connection").change(change_data);

        $('#device_form').submit(function(event) {
            var data = '';
            $('.join_field').each(function(i) {
                data += '"' + $(this).attr('id').substring('join_'.length) + '"'
                data += ':'
                data += '"' + $(this).val() + '",'
            });
            $('#id_data').val('{' + data.substring(0,data.length-1) + '}');

            return;
        });
    }
});
