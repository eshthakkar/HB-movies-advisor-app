
"use strict";

$('select[multiple]').multiselect({
    columns: 1,
    placeholder: 'Select options',
    selectAll : true
});

function showMovieResults(results){
  //Display movie thumbnails for the selected genre/genres 

  $('#thumbnails').empty();
  for (var movieid in results) {
    var thumbnail_url = results[movieid];
    $('<div class="image-container"><img src=' + thumbnail_url + ' data-toggle="modal" data-target=".bs-example-modal-lg" class="image" id=' + movieid + '><div class="addbutton btn btn-default" id=button_' + movieid + '>Add</div></div>').appendTo('#thumbnails');

  }
  $('.image').on('click',showDetails);
  $('.image-container').on('mouseover',showbuttons);
  $('.image-container').on('mouseout',hidebuttons);
  $('.addbutton').on('click',showWatchList);

}

function showbuttons(){
  $(this).find('.addbutton').css('display','inline');
}

function hidebuttons(){
  $(this).find('.addbutton').css('display','none');
}

function showWatchList(){
  console.log("I was clicked");
  var m = $(this).attr('id');
  console.log(m);
  


}
function sendGenre(){
  // Send selected genre/genres and ratings to the browse.json route

  var selections = $('.chk:checked').map(function() {return this.value;}).get();
  var rating = $('#slider').val();

  var filterCriteria = {
    "genre" : selections,
    "rating": parseFloat(rating)
  };

  $.get("/browse.json",filterCriteria,showMovieResults);

}

function showDetails(){
  // Show details related to a movie

  var mid = $(this).attr('id');
  $.get("/movie.json/" + mid,function(results){
    $('#myModalLabel').html(results["title"]);

    $('#rating').html("imdb rating: " + results["imdb_rating"]);
    $('#release').html("Released On: " + results["released_at"]);
    $('#runtime').html("Runtime: " + results["runtime"]);
    $('#actors').html("Actors: " + results["actors"]);

    $("#genres").empty();
    for(var i=0; i < results["genres"].length; i++){
      $("#genres").append("<li>" + results["genres"][i] + "</li>");
    }

    $("#sources").empty();
    for (var k in results["sources"]){
      $("#sources").append('<a href=' + results["sources"][k] + '><button>' + k + '</button></a>')
    }


    $('#synopsis p').html(results["plot"]);
    $('#poster img').attr('src',results["poster_url"]);

  });
}

// Event when checkbox or slider value changes
$('#check, #slider').change(sendGenre);

// update slider text value while sliding
$('#slider').on('input',function(){
  $('#range').html(this.value);
});







