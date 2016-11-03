
"use strict";

function showMovieResults(results){
  //Display movie thumbnails for the selected genre 

  for (var movieid in results) {
    var thumbnail_url = results[movieid];

    // If there are no thumbnails, add thumbnail
    if($('#thumbnails').html() === ""){
      $('<img src=' + thumbnail_url + '>').appendTo('#thumbnails');
    }

    // if thumbnails already exist on the page
    else{
        // create a dictionary of existing thumbnails on page
      var dict = {};
      var count = 0;
      $("#thumbnails > img").each(function(){
        dict[$(this).attr('src')] = count;
        count++;
      })

      // compare current thumbnail with existing thumbnails,
      // if its not on page, only then add it to the page

      if (!(thumbnail_url in dict)){
        $('<img src=' + thumbnail_url + '>').appendTo('#thumbnails');
      }
    }
  }
}

function sendGenre(){
  // Send selected genre to the browse.json route

  var checkedGenre = {
    "genre": $(this).val()
  };

  if($(".chk").is(':checked')){
    $.post("/browse.json",checkedGenre,showMovieResults);
  }
  else{
     $('#thumbnails').empty();
  }
}

$('.chk').change(sendGenre);


