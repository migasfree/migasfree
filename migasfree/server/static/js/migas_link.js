function dropdown_migas_link(app, model, pk) {
    $.get( "/link/?app="+app+"&model="+model+"&pk="+pk, function( data ) {
        $("#"+app+"-"+model+"-"+pk).html(data);
        $('ul[name='+app+'-'+model+'-'+pk).html(data);
    });
}
