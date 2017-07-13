
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
                       scale:true,
				type : 'value'
			}
		],
		series : [
			{
				"name":'价格',
				"type":"line",
				"data":result.y,
                    markPoint: {
                        data: [
                            {type: 'max', name: '最大值'},
                            {type: 'min', name: '最小值'}
                        ]
                    },
                    markLine: {
                        data: [{
        name: 'Y 轴值为 100 的水平线',
        yAxis: 2101
    }]
                    }
			}
		]
	};
	// 为echarts对象加载数据
	myChart.setOption(option);
}

