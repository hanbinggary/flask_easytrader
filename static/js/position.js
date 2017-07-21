getstockinfo();

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

function getstockinfo () {
	var myDate = new Date();
	if (checkTradeTime())
	{
		setTimeout(getstockinfo,50000);
	}
	$.ajax({
		type: "GET",
		url: "/positionhuatai/",
		success: function(msg){
                $('#position').html(msg);
		},
		error:function(){
                $('#position').html("error");
			},
		})
}