
"use strict";

function showMovieResults(results){
  //Display movie thumbnails for the selected genre/genres 
  $('#thumbnails').empty();
  for (var movieid in results) {
    var thumbnail_url = results[movieid];
    $('<img src=' + thumbnail_url + ' class="image" id=' + movieid + '>').appendTo('#thumbnails');
  }
  $('.image').on('click',showDetails);
}

function sendGenre(){
  // Send selected genre/genres to the browse.json route

  var selections = $('.chk:checked').map(function() {return this.value;}).get();
  var checkedGenre = {
    "genre" : selections
  };

  $.post("/browse.json",checkedGenre,showMovieResults);

}

function showDetails(){
  console.log($(this).attr('id'));
}

$('.chk').change(sendGenre);







