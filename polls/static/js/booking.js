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
			$("#url+.invalid-feedback").text($("#url+.invalid-feedback").data("text"));
			return false;
		}
        if($("#url").val().indexOf('https://www.booking.com') != -1){

        }else{
            $("#url").addClass("is-invalid");
            return false;
        }
        $("#url").removeClass("is-invalid");
        $("#fetch_btn i").addClass("fa-spin");
        $("#result-status").removeClass("no-data data-loaded").addClass("data-loading");
        $('#fetch_btn').addClass("disabled");
        
		var response= '';
		$('#result_data tbody').html('');
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
                        if(data.length == 0){
                            $("#url").addClass("is-invalid");
                            $("#url+.invalid-feedback").text("URLが正しくないです。Booking.comの検索結果URLをご入力してください。");
                            $("#result-status").removeClass("data-loaded data-loading").addClass("no-data");
                            return;
                        }
                        
                        
                        var resp = data;
                        for (var i = 0; i <= resp.length - 1; i++) {
                            var dateTmp = new Date(resp[i].check_in_date);
                            var dateTmpOut = new Date(resp[i].check_out_date);
                            var flag = 0;
                            for(var j=0; j<= resp[i].room_data.length -1; j++){
                                append_data+="<tr>";
                                if(flag == 0){
                                    flag = 1;
                                    append_data+="<td>"+(dateTmp.getMonth()+1) + "月" + dateTmp.getDate() + "日</td>";
                                    append_data+="<td>"+(dateTmpOut.getMonth()+1) + "月" + dateTmpOut.getDate() + "日</td>";
                                    append_data+="<td>"+resp[i].name+"</td>";
                                    append_data+="<td>"+resp[i].rating+"</td>";
                                    append_data+="<td>"+resp[i].address+"</td>";
                                }else{
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                }
                                
                                append_data+="<td>"+ resp[i].room_data[j].room_type +"</td>";
                                append_data+="<td>"+ resp[i].room_data[j].capacity +"</td>";
                                if(resp[i].room_data[j].is_available == 'true'){
                                    append_data+="<td>"+ resp[i].room_data[j].occupancy +"</td>";
                                    append_data+="<td>"+ resp[i].room_data[j].pricing +"</td>";
                                }else{
                                    append_data+="<td></td>";
                                    append_data+="<td>"+ resp[i].room_data[j].occupancy +"</td>";
                                }
                                
                                append_data+="<td class='altclass hideme'>"+resp[i].URL+"</td>";
                                append_data+="</tr>";
                            }
                            
                        }

                        $("#result-status").removeClass("data-loading no-data").addClass("data-loaded");
                    }catch(e){
                        console.log(e);
                        $("#fetch_btn i").removeClass("fa-spin");
                        if (e instanceof SyntaxError) {
                            $("#url").addClass("is-invalid");
                            $("#url+.invalid-feedback").text("URLが正しくないです。Booking.comの検索結果URLをご入力してください。");
                        } else {
                            $("#url").addClass("is-invalid");
                            $("#url+.invalid-feedback").text("URLが正しくないです。Booking.comの検索結果URLをご入力してください。");
                        }
                        $("#result-status").removeClass("data-loaded data-loading").addClass("no-data");
                    }
                    
                    console.log("Success");
                },
                error: function(resp){
                    console.log("Error");
                    // TODO
                    $("#invalid-feedback").text("URLが正しくないです。Booking.comの検索結果URLをご入力してください。");
                    $("#fetch_btn i").removeClass("fa-spin");
                    $('#fetch_btn').removeClass("disabled");
                    $("#result-status").removeClass("data-loaded data-loading").addClass("no-data");
                }
            }).done(function(){
                    console.log("Done");
				$('#result_data tbody').html('');
				$('#result_data tbody').append(append_data);
                $("#fetch_btn i").removeClass("fa-spin");
                $('#fetch_btn').removeClass("disabled");
		});
	});

	$(document).on('click','#import',function(){
		$('.altclass').removeClass('hideme');
		$("#result_data").table2csv({
		  filename: 'table.csv'
		});
		$('.altclass').addClass('hideme');

	});

	$('#loginForm').submit(function(){
		var resp = '';
		$("#login_button i").addClass("fa-spin fa-refresh");
		$("#login_button i").removeClass("fa-sign-in");
        
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
					$("#login_button i").addClass("fa-sign-in");
					$("#login_button i").removeClass("fa-spin fa-refresh");
				}
		});
        return false;
	});

    /**
     * MULTIPLE INPUT FILEDS JS
    */
    $(document).on('click','.addField',function(){
        var data = '<div class="input-group mb-3 hotelurl">';
            data += '<input type="text" class="form-control" placeholder="ホテルのURL" aria-label="ホテルのURL" aria-describedby="basic-addon2">';
            data += '<div class="input-group-append">';
            data += '<span class="input-group-text addField pointer" id="">+</span>';
            data += '</div>';
            data += '<div class="invalid-feedback" data-text="Booking.comに検索してURLをご入力してください"></div>';
            data += '</div>';
        $(this).html('-');
        $(this).removeClass('addField');
        $(this).addClass('removeField');
        $('.urllist').append(data);
        //
    });

    $(document).on('click','.removeField',function(){
        $(this).closest('.hotelurl').remove();
    });

    /**
     * FETCHING DATAS BY HOTEL URLs
    */
    $(document).on('click','#fetch_hotel',function(){
        var hotel_urls = [];
        var url_list = $('.urllist input');
        var error_flag = 0;
        $.each(url_list,function(k,v){
            if($.trim($(v).val()) == ''){
                $(v).addClass("is-invalid");
                error_flag++;
                //return false;
            }
            if($(v).val().indexOf('https://www.booking.com') != -1){
                //return false; 
            }else{
               $(v).addClass("is-invalid");
               error_flag++;
               //return false;
            }
            hotel_urls.push($(v).val())
        });
        if(error_flag > 0){
            return false;
        }
        console.log(hotel_urls);
        $("#fetch_hotel i").addClass("fa-spin");
        $("#fetch_hotel i").addClass("disabled");
        /**START AJAX**/
        var range = $("#daterange").val();
        var split_date = range.split('-');
        var from_date = split_date[0].split('/');
        var to_date = split_date[1].split('/');
        var checkin = from_date[2]+'-'+from_date[0]+'-'+from_date[1];
        var checkout = to_date[2]+'-'+to_date[0]+'-'+to_date[1];

        checkin = checkin.replace(' ','');
        checkout = checkout.replace(' ','');
        var append_data ='';
        $.ajax({
                url:'scrap_list',
                type:'POST',
                cache:false,
                data:{
                    url:JSON.stringify(hotel_urls),
                    checkin:checkin,
                    checkout:checkout,
                    csrfmiddlewaretoken:$('input[name="csrfmiddlewaretoken"]').val()
                },
                datatype: 'json',
                "async": true,
                "crossDomain": true,
                success: function (data) {
                    var resp = data;
                    // console.log(resp.length)
                        for (var i = 0; i <= resp.length - 1; i++) {
                            console.log('here');
                            var dateTmp = new Date(resp[i].check_in_date);
                            var dateTmpOut = new Date(resp[i].check_out_date);
                            var flag = 0;
                            for(var j=0; j<= resp[i].room_data.length -1; j++){
                                append_data+="<tr>";
                                if(flag == 0){
                                    flag = 1;
                                    append_data+="<td>"+(dateTmp.getMonth()+1) + "月" + dateTmp.getDate() + "日</td>";
                                    append_data+="<td>"+(dateTmpOut.getMonth()+1) + "月" + dateTmpOut.getDate() + "日</td>";
                                    append_data+="<td>"+resp[i].hotel_name+"</td>";
                                    append_data+="<td>"+resp[i].rating+"</td>";
                                    append_data+="<td>"+resp[i].hotel_address+"</td>";
                                }else{
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                    append_data+="<td></td>";
                                }
                                
                                append_data+="<td>"+ resp[i].room_data[j].room_type +"</td>";
                                append_data+="<td>"+ resp[i].room_data[j].capacity +"</td>";
                                if(resp[i].room_data[j].is_available == 'true'){
                                    append_data+="<td>"+ resp[i].room_data[j].occupancy +"</td>";
                                    append_data+="<td>"+ resp[i].room_data[j].pricing +"</td>";
                                }else{
                                    append_data+="<td></td>";
                                    append_data+="<td>"+ resp[i].room_data[j].occupancy +"</td>";
                                }
                                
                                //append_data+="<td class='altclass hideme'>"+resp[i].URL+"</td>";
                                append_data+="</tr>";
                            }
                            
                        }

                        // $("#result-status").removeClass("data-loading no-data").addClass("data-loaded");
                }
            }).done(function(){
                $('#result_data tbody').html('');
                $('#result_data tbody').append(append_data);
                $("#fetch_hotel i").removeClass("fa-spin");
                $('#fetch_hotel').removeClass("disabled");
                $("#result-status").removeClass("data-loading no-data").addClass("data-loaded");

            });
    });
    /**END AJAX FOR HOTEL WISE SEARCH**/
});