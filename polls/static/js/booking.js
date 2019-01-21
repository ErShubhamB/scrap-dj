$(document).ready(function(){
    if($('#daterange').length > 0){
    	$('#daterange').daterangepicker({
        "locale": {
        "format": "MM/DD/YYYY",
        "separator": " - ",
        "applyLabel": "適用する",
        "cancelLabel": "キャンセル",
        "fromLabel": "から",
        "toLabel": "に",
        "customRangeLabel": "カスタム",
        "daysOfWeek": [
            "日",
            "月",
            "火",
            "水",
            "木",
            "金",
            "土"
        ],
        "monthNames": [
            "1月",
            "2月",
            "3月",
            "4月",
            "5月",
            "6月",
            "7月",
            "8月",
            "9月",
            "10月",
            "11月",
            "12月"
        ],
        "firstDay": 1
    }
		});
    }
	

	$(document).on('click','#fetch_btn',function(){
		if($.trim($("#url").val()) == ''){
			$("#url").addClass("is-invalid");
			return false;
		}
        if($("#url").val().indexOf('https://www.booking.com') != -1){

        }else{
            $("#url").addClass("is-invalid");
            return false;
        }
        $("#url").removeClass("is-invalid");
        $("#fetch_btn i").addClass("fa-spin");
        
        
		var response= '';
		$('#result_data tbody').html('');
		$('#result_data tbody').append('<tr class="text-center"><td colspan="6">暫くお待ちください。。。</td></tr>');
		var append_data = '';
		var range = $("#daterange").val();
		var split_date = range.split('-');
		var from_date = split_date[0].split('/');
		var to_date = split_date[1].split('/');
		var checkin = from_date[2]+'-'+from_date[0]+'-'+from_date[1];
		var checkout = to_date[2]+'-'+to_date[0]+'-'+to_date[1];

		checkin = checkin.replace(' ','');
		checkout = checkout.replace(' ','');
		$.ajax({
                url:'data_fetch',
                type:'GET',
                cache:false,
                data:{
                	url:$("#url").val(),
                	checkin:checkin,
                	checkout:checkout
                },
                datatype: 'json',
                "async": true,
  				"crossDomain": true,
                success: function (data) {
                    try{
                        var resp = data;
                        for (var i = resp.length - 1; i >= 0; i--) {
                        var pr= '';
                        if(resp[i].price == ''){
                            pr = 'XXX';
                        }else{
                            pr = resp[i].price;
                        }
                    	append_data+="<tr>";
                    	append_data+="<td>"+resp[i].check_in_date+" to "+resp[i].check_out_date+"</td>";
                    	append_data+="<td>"+resp[i].name+"</td>";
                    	append_data+="<td>"+pr+"</td>";
                    	append_data+="<td>"+resp[i].rating+"</td>";
                    	append_data+="<td>"+resp[i].address+"</td>";
                    	append_data+="<td>"+resp[i].occupancy+"</td>";
                    	append_data+="</tr>";
                    }
                    }catch(e){
                        $("#fetch_btn i").removeClass("fa-spin");
                        if (e instanceof SyntaxError) {
                            alert('Looks like the URL you entered is not returning proper data. Please try changing the URL.')
                        } else {
                            //console.log(e, false);
                            alert('Looks like the URL you entered is not returning proper data. Please try changing the URL.')

                        }
                    }
                    

                },
                error: function(resp){
                    // TODO
                    alert('Looks like the URL you entered is not returning proper data. Please try changing the URL.')
                    $("#fetch_btn i").removeClass("fa-spin");
                }
            }).done(function(){
				$('#result_data tbody').html('');
				$('#result_data tbody').append(append_data);
                $("#fetch_btn i").removeClass("fa-spin");
                $('#import').removeClass('show-on-data-load');
		});
	});

	$(document).on('click','#import',function(){
		$('.altclass').removeClass('hideme');
		$("table").table2csv({
		  filename: 'table.csv'
		});
		$('.altclass').addClass('hideme');

	});

	$(document).on('click','#login_buttton',function(){
		var resp = '';
		$("#login_buttton i").addClass("fa-spin fa-refresh");
		$("#login_buttton i").removeClass("fa-sign-in");
		$.ajax({
                url:'user_login',
                type:'POST',
                data: {
		          'username': $("#userid").val(),
		          'password' : $("#password").val(),
                  'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val()
		        },
                cache:false,
                datatype: 'json',
                "async": true,
  				"crossDomain": true,
                success: function (data) {
                   resp = data;
                },
                error: function(resp){
                    
                }
            }).done(function(){

				if(resp.status == 200){
					window.location.href= '/';
				}else{
					$('#error').removeClass('hideme');
					$("#login_buttton i").addClass("fa-sign-in");
					$("#login_buttton i").removeClass("fa-spin fa-refresh");
				}
		});
	});
});
