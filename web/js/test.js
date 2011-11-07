
$.postJSON = function(url, data, callback) {
	$.ajaxSetup({ scriptCharset:"utf-8", 
					contentType:"application/json; charset=utf-8" });
	$.post(url, $.toJSON(data), callback, "json");
}

$(document).ready(function() {
	$("#register, #login").click(function(e) {
		$.postJSON('test', {'test':'ok'}, function(data) {alert(data.message);});
		return e.preventDefault();
	});
});

