$(document).ready(function(e) {
    $("#run").click(function(e) {
        document.getElementById('hide').style.display='none';
        alert('asdasd')
		alert(convertTableToJson())
		})
});

    var convertTableToJson = function()
        {
			var ch=document.getElementById("title").value;
			var x=document.getElementById("year").value;
			var y=document.getElementById("genres").value;
			//var z=document.getElementById("reviewStars-input").value;
			$("#title").text();
			$("#year").text();
			$("#genres").text();
			//$("#userRating").text();

            var rows = [];
            $('tr.tr1').each(function(i, n){
                var $row = $(n);
                rows.push({
                    title:		ch,//$row.find('td:eq(0)').text(),
                    year:  	 x,//$row.find('td:eq(1)').text(),
                    genres:   	 y,//$row.find('td:eq(2)').text(),
                    //userRating:   	 z,//$row.find('td:eq(3)').text(),
                });
            });
            return JSON.stringify(rows);
        };
