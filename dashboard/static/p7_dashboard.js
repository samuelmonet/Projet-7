// contient les articles de presse, qui doivent être 
// gardés en mémoire même après affichage du graphique
var news_data;

// Palette de couleurs utilisée par tous les graphiques
var colors = ['#006600', '#009900', '#00CC00', '#00FF00','#80FF00','#FFFF00','#FF9933','#FF3333','#FF0000','#CC0000','#800000'];

var colors_educ = new Map();
colors_educ.set("Lower secondary", '#CC0000');
colors_educ.set('Secondary / secondary special', '#FF9933');
colors_educ.set('Incomplete higher', '#FFFF00');
colors_educ.set('Higher education', '#00FF00');
colors_educ.set('Academic degree', '#006600');

// Chargement des info clients
$.ajax({
          url: "/info/client/",
          success: infos
});

$.ajax({
          url: "/info/loan/",
          success: ratios
});

$.ajax({
          url: "/info/rate/",
          success: rates
});

// Chargement et traitement des données ext avec nvd3
d3.json('/info/ext1/', display_ext1_graph);
d3.json('/info/ext2/', display_ext2_graph);
d3.json('/info/ext3/', display_ext3_graph);

function ratios(result) {
         data_ratio=result['data'];
         if (Math.abs(data_ratio['ref']-data_ratio['cli'])>Math.abs(data_ratio['acc']-data_ratio['cli'])) {
	 var couleur='green'
	 } else {
	 var couleur='red'
	 }
	 Highcharts.chart('container', {
    	 chart: {
        	type: 'bar'
    	},
    	title: {
        	text: 'Ratio montant du pret - cout du bien'
    	},
    	xAxis: {
        	categories: ['Moyenne Prêts Acceptés', 'Valeur Client','Moyenne Prêts Refusés',]
    	},
    	yAxis: {
        	min: 0,
        	title: {
            	text: 'Montant du prêt/Cout du bien à acheter'
        	}
    	},   	
    	legend: {
        enabled: false
    	},   	
    	plotOptions: {
    	    series: {
    	        stacking: 'normal'
    	    }
    	},   	   	
    	series: [{
        name: 'Moyenne Prêts Acceptés',
        data: [data_ratio['acc'],0,0],
        color:"#999999"
    }, {
        name: 'Moyenne Prêts Refusés',
        data: [0,0,data_ratio['ref']],
        color: "#000000"
    }, {
        name: 'Client',
        data: [0,data_ratio['cli'],0],
        color: couleur
    }]
	});
};

function rates(result) {
         data_rates=result['data'];
         if (Math.abs(data_rates['ref']-data_rates['cli'])>Math.abs(data_rates['acc']-data_rates['cli'])) {
	 var couleur='green'
	 } else {
	 var couleur='red'
	 }
	 Highcharts.chart('container2', {
    	 chart: {
        	type: 'bar'
    	},
    	title: {
        	text: 'Montant des annuités: Pourcentage du crédit total'
    	},
    	xAxis: {
        	categories: ['Moyenne Prêts Acceptés', 'Valeur Client','Moyenne Prêts Refusés',]
    	},
    	yAxis: {
        	min: 0,
        	title: {
            	text: 'Montant du prêt/Cout du bien à acheter'
        	}
    	},   	
    	legend: {
        enabled: false
    	},   	
    	plotOptions: {
    	    series: {
    	        stacking: 'normal'
    	    }
    	},
    	
    	   	
    	series: [{
        name: 'Moyenne Prêts Acceptés',
        data: [data_rates['acc'],0,0],
        color:"#999999"
    }, {
        name: 'Moyenne Prêts Refusés',
        data: [0,0,data_rates['ref']],
        color: "#000000"
    }, {
        name: 'Client',
        data: [0,data_rates['cli'],0],
        color: couleur
    }]
	});
};


function infos(result) {
         info=result['data'];
	display_result(info);
};

function display_result(info) {

	var client_id=info['client_id'];
	document.getElementById('client_id').innerHTML=client_id;

	var score=Math.round(info['score']);
	document.getElementById('score').innerHTML=score;
	if (score>56) {
		document.getElementById('score').style.color = 'green';
	} else  if (score>48){
		document.getElementById('score').style.color = '#80FF00';
	}
	else {
		document.getElementById('score').style.color = 'red';
	}

	var credit=info['CREDIT'];
	document.getElementById('credit').innerHTML=Math.round(credit);
	if (info['CREDIT']>info['PRICE']) {
		document.getElementById('credit').style.color = 'red';
	} else {
		document.getElementById('credit').style.color = 'green';
	}
	console.log(credit)
	var price=Math.round(info['PRICE']);
	document.getElementById('prix').innerHTML=price;
	console.log(price)
	var annuit=Math.round(info['ANNUITY']);
	document.getElementById('annuite').innerHTML=annuit;
	console.log(annuit)
	

	if (info['GENDER']=="M") {
		var sexe='Male';
		document.getElementById('sexe').style.color = 'red';
	} else {
		var sexe='Female';
		document.getElementById('sexe').style.color = 'green';
	}
	document.getElementById('sexe').innerHTML=sexe;

	var age=info['AGE'];
	document.getElementById('age').innerHTML=age;

	var taf=info['YEARS EMPLOYED'];
	document.getElementById('taf').innerHTML=taf;

	var educ=info['EDUCATION'];
	document.getElementById('education').innerHTML=educ;
	document.getElementById('education').style.color = colors_educ.get(educ);

	var children=info['CHILDREN'];
	document.getElementById('children').innerHTML=children;

	var family=info['FAMILY SIZE'];
	document.getElementById('family').innerHTML=family;

	if (info['CAR']=="Y") {
		if (!info['CAR AGE']) {
			var voiture = 'Age inconnu';
			} else {
			var age='Age ='
			var voiture=age.concat(' ',info['CAR AGE'].toString());						
		} 
	} else {
		var voiture='Pas de voiture'		
	} 
	document.getElementById('voiture').innerHTML = voiture;

	var debt=info['bb_debt'];
	document.getElementById('bb').innerHTML=debt;
	if (debt>0) {
		document.getElementById('bb').style.color = 'red';
	} else {
		document.getElementById('bb').style.color = 'green';
	}
	
	if (!info['bb_debt']) {
		var debt=0;
	} else {
		var debt=Math.round(info['bb_debt']);
	}
	if (debt>0) {
		document.getElementById('bb').style.color = 'red';
	} else {
		document.getElementById('bb').style.color = 'green';
	}
	document.getElementById('bb').innerHTML=debt;
	
	if (!info['INST_days_diff_max']) {
		var retard=0;
	} else {
		var retard=-info['INST_days_diff_max'];
	}
	if (retard>0) {
		document.getElementById('inst').style.color = 'red';
	} else {
		document.getElementById('inst').style.color = 'green';
	}
	document.getElementById('inst').innerHTML=retard;
	
	if (!info['CAR AGE']) {
		var card=0;
	} else {
		var card=info['CC_AMT_%'];
	}
	if (card>0) {
		document.getElementById('card').style.color = 'red';
	} else {
		document.getElementById('card').style.color = 'green';
	}
	document.getElementById('card').innerHTML=card;
	
	if (!info['EXT_1']) {
		document.getElementById('ext1').innerHTML = 'No information available';
	}
	if (!info['EXT_2']) {
		document.getElementById('ext2').innerHTML = 'No information available';
	}
	if (!info['EXT_3']) {
		document.getElementById('ext3').innerHTML = 'No information available';
	}

};


var getColorArray = function(n,ext) {
	col_array=[];
	
	for (var i=0; i<n;i++){
		if (i==Math.floor(ext/0.025)){
		col='#000080'
		col_array.push(col);
		} else {
		col=colors[10-Math.floor(i/(n/10))];
		col_array.push(col);
		}
	}
	return col_array;
}

		 
function display_ext1_graph(data1) {
    if (data1["status"] == "ok") {
        ext1 = [{key: 'Source_1',values: data1["data"]}]
	var ext=data1['ext']
	if (ext===0){
		document.getElementById('chart1').innerHTML='No information available';
		} else {
	        nv.addGraph(function() {
        	    var chart = nv.models.discreteBarChart()
        	      	.x(function(d) { return d[0] })    //Specify the data accessors.
			.y(function(d) { return d[1] })
      			.staggerLabels(false)    //Too many bars and not enough room? Try staggering labels.
      			.showValues(false)       //...instead, show the bar value right on top of each bar.
        	    	.showXAxis(false)
        	    	.showYAxis(false)
        	    	.color(getColorArray(40,ext))
        	    	chart.tooltip.enabled(true)               
        	    d3.select('#chart1 svg')
      			    .datum(ext1)
      			    .call(chart);
        	    nv.utils.windowResize(chart.update);
        	    return chart;
        	});
        }
    }
};

function display_ext2_graph(data2) {
    if (data2["status"] == "ok") {
        ext2 = [{key: 'Source_2',values: data2["data"]}]
	var ext=data2['ext']
	if (ext===0){
		document.getElementById('chart2').innerHTML='No information available';
		} else {
	        nv.addGraph(function() {
        	    var chart = nv.models.discreteBarChart()
        	      	.x(function(d) { return d[0] })    //Specify the data accessors.
			.y(function(d) { return d[1] })
      			.staggerLabels(false)    //Too many bars and not enough room? Try staggering labels.
      			.showValues(false)       //...instead, show the bar value right on top of each bar.
        	    	.showXAxis(false)
        	    	.showYAxis(false)
        	    	.color(getColorArray(40,ext))
        	    	chart.tooltip.enabled(true)               
        	    d3.select('#chart2 svg')
      			    .datum(ext2)
      			    .call(chart);
        	    nv.utils.windowResize(chart.update);
        	    return chart;
        	});
        }
    }
};

function display_ext3_graph(data3) {
    if (data3["status"] == "ok") {
        ext3 = [{key: 'Source_3',values: data3["data"]}]
	var ext=data3['ext']
	if (ext===0){
		document.getElementById('chart3').innerHTML='No information available';
		} else {
	        nv.addGraph(function() {
        	    var chart = nv.models.discreteBarChart()
        	      	.x(function(d) { return d[0] })    //Specify the data accessors.
			.y(function(d) { return d[1] })
      			.staggerLabels(false)    //Too many bars and not enough room? Try staggering labels.
      			.showValues(false)       //...instead, show the bar value right on top of each bar.
        	    	.showXAxis(false)
        	    	.showYAxis(false)
        	    	.color(getColorArray(40,ext))
        	    	chart.tooltip.enabled(true)               
        	    d3.select('#chart3 svg')
      			    .datum(ext3)
      			    .call(chart);
        	    nv.utils.windowResize(chart.update);
        	    return chart;
        	});
        }
    }
};
