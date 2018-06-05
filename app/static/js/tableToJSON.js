$(document).ready(function(e) {
    $("#run").click(function(e) {
//        document.getElementById('hide').style.display='none';
        alert('asdasd')
		alert(convertTableToJson())
		})
});

    var convertTableToJson = function()
        {
			var ch=document.getElementById("id").value;
//			var x=document.getElementById("year").value;
//			var y=document.getElementById("genres").value;
			//var z=document.getElementById("reviewStars-input").value;
			$("#id").text();
//			$("#year").text();
//			$("#genres").text();
			//$("#userRating").text();
			var userRating;
			var isChecked=true;
			switch(isChecked){
			    case 'getElementById("star-10{{item.id}}").checked':
			        userRating = 10
			        [break]
			    case 'getElementById("star-9{{item.id}}").checked':
			        userRating = 9
			        [break]
			    case 'getElementById("star-8{{item.id}}").checked':
			        userRating = 8
			        [break]
			    case 'getElementById("star-7{{item.id}}").checked':
			        userRating = 7
			        [break]
			    case 'getElementById("star-6{{item.id}}").checked':
			        userRating = 6
			        [break]
			    case 'getElementById("star-5{{item.id}}").checked':
			        userRating = 5
			        [break]
			    case 'getElementById("star-4{{item.id}}").checked':
			        userRating = 4
			        [break]
			    case 'getElementById("star-3{{item.id}}").checked':
			        userRating = 3
			        [break]
			    case 'getElementById("star-2{{item.id}}").checked':
			        userRating = 2
			        [break]
			    case 'getElementById("star-1{{item.id}}").checked':
			        userRating = 1
			        [break]
			}
			$("userRating").text();

            var rows = [];
            $('tr.tr1').each(function(i, n){
                var $row = $(n);
                rows.push({
                    id:		ch,//$row.find('td:eq(0)').text(),
//                    year:  	 x,//$row.find('td:eq(1)').text(),
//                    genres:   	 y,//$row.find('td:eq(2)').text(),
                    userRating:   	 userRating,//$row.find('td:eq(3)').text(),
                });
            });
            return JSON.stringify(rows);
        };
