getstockinfo($("#hidstockno").val());

function checkTradeTime(){
	var myDate = new Date();
	arr = ['9','10','11','13','14'];
	for (var k = 0, length = arr.length; k < length; k++)
	{
		if (myDate.getHours()==arr[k])
		{
			return true;
		}
	}
	return false;
}

function getstockinfo (stockno) {
	//var myDate = new Date();
	if (checkTradeTime())
	{
		setTimeout(function(){getstockinfo(stockno);},9000);
	}
	$.ajax({
		type: "GET",
		url: "/hangqingsub/" + stockno,
		success: function(msg){
                $('#stock_info').html(msg);
		},
		error:function(){
                $('#stock_info_error').html("error");
			},
		})
}