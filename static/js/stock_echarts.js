
GetMinLine();

function GetMinLine(){
	$.ajax({
	  type:"GET",
	  url: "/getminline/000001", // + stockno,
	  success:function(result){
		if (result) {
		  SetChart(jQuery.parseJSON(result.replace(/'/g,'"')));
		}
	  },
		error : function(errorMsg) {
			alert("sorry，请求数据失败");
			//myChart.hideLoading();
		}
	})
}
function SetChart(result){
  var  myChart = echarts.init(document.getElementById('main_charts'));
  var  option = {
    title: {
        text: ''
    },
		tooltip: {
			show: true
		},
		legend: {
		   data:['价格']
		},
		xAxis : [
			{
				type : 'category',
				data : result.x
			}
		],
		yAxis : [
			{
				type : 'value'
			}
		],
		series : [
			{
				"name":'series',
				"type":"line",
				"data":result.y
			}
		]
	};
	// 为echarts对象加载数据
	myChart.setOption(option);
}

