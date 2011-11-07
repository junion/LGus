$(document).ready(function() {
	$("#register, #login").click(function(e) {
		var name = ($(event.target).attr('id') == 'register') ? 'Registration' : 'Login';
		$('#message').slideUp('fast');
		
		var param = $('#mainform').serializeObject();
		param['action'] = $(event.target).attr('id');
		$.ajax({
			type:'POST',
			url:'services/rest/register', 
			contentType:'application/json', 
			processData:false, 
			data:JSON.stringify(param), 
			success:function(data) {
				var obj = $.parseJSON(data);
				switch(obj.err_id) {
					case 0:
						$('#message').addClass('success');
						$('#message').slideDown('fast');
						window.location.href="start_over';
						break;
					case 1:
						$('#message').html('The username is invalid.');
						break;
					case 2:
						$('#message').html('The password must be longer than 4 characters.');
						break;
					case 3:
						$('#message').html('The passwords you entered do not match.');
						break;
					case 4:
						$('#message').html('The first name is invalid.');
						break;
					case 5:
						$('#message').html('The last name is invalid.');
						break;
					case 6:
						$('#message').html('The email entered is invalid.');
						break;
					case 7:
						$('#message').html('This username has already been taken. Try some of these suggestions:<br/><br/>');
						break;
					case 8:
						$('#message').html('The username is invalid.');
						break;
					case 9:
						$('#message').html('The password is invalid.');
						break;
					default:
						$('#message').html('An error occurred, please try again.');
				}
				$('#message').addClass('error');
				$('#message').slideDown('fast');
			}, 
			dataType:'application/json'
		});
		return e.preventDefault();
	});
});
