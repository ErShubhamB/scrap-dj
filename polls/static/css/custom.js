$(document).ready(function(){
	$('#daterange').daterangepicker({
		},
		function(start, end, label) {
		    alert("A new date range was chosen: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
	});

	$(document).on('click','#fetch_btn',function(){
		console.log('here');
		var response= '';
		$('#result_data tbody').html('');
		$('#result_data tbody').append('<tr><td colspan="6">Please wait.. Loading data.</td></tr>');
		$.ajax({
                url:'/booking-com.php',
                type:'POST',
                cache:false,
                datatype: 'json',
                data: {'url':$("#url").val()} ,
                success: function (data) {
                    response = resp;
                },
                error: function(resp){
                    
                }
            }).done(function(){

		});
	});
});