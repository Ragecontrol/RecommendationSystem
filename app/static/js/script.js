function funcStars(numStar, idItem, title) {
    var star = document.getElementById("star-" + numStar + idItem);
    var value = star.value;

   $.ajax({
       url: '/saveStars/' + value+'/'+idItem+'/'+title,
//       data:
//       headers: {
//       'countStar': value
//       },
       type: 'GET',
       success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
   })
}