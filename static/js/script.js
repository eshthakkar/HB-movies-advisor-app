
"use strict";

function showMovieResults(results){
  for (var key in results) {
    var value = results[key];
    console.log(value)
    $('<img src=' + value + '>').appendTo('#movies');
  }
}

function sendinfo(){
  var checkInput = {
    "genre": $(this).val()
  };

  $.post("/browse",checkInput,showMovieResults);
}

$('.chk').change(sendinfo);


