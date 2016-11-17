
"use strict";

$('select[multiple]').multiselect({
    columns: 1,
    placeholder: 'Select options',
    selectAll : true
});

function showMovieResults(results){
  //Display movie thumbnails for the selected genre/genres 
  $('#thumbnails').empty();
  $('#movie_add_resp').empty();

  for (var movieid in results) {
    var thumbnail_url = results[movieid];
    $('<div class="image-container"><img src=' + thumbnail_url + ' data-toggle="modal" data-target=".bs-example-modal-lg" class="image" id=' + movieid + '> \
      <div class="addbutton btn btn-default" data-toggle="modal" data-target="#myModal" data-backdrop="static" data-keyboard="false" id=button_' + movieid + '>Add</div></div>').appendTo('#thumbnails');

  }
  $('.image').on('click',showDetails);
  $('.image-container').on('mouseover',showbuttons).on('mouseout',hidebuttons);
  $('.addbutton').on('click',addMovieToWatchList);

}

function showbuttons(){
  // Show add buttons on top of thumbnail
  $(this).find('.addbutton').css('display','inline');
}

function hidebuttons(){
  // Hide add button which displayed on top of thumbnail
  $(this).find('.addbutton').css('display','none');
}

function addMovieToWatchList(){
  // Add the movie to user's watch list
  var movie_to_add = {
    "movie_identifier": $(this).attr('id')
  };

  $.post('/watchlist',movie_to_add,function(result){
    console.log(result);

    // Updates the response text in modal window for all cases
    $('#myModalLabelQuiz').html(result.text);

    // Disables add button when a movie was successfully added or the movie to
    // be added exists in watch list already
    if(result.status === "success" || result.status === "prevent"){
      $('#button_' + result.id).attr("disabled",true); 
    }

    // Display question and form when movie is successfully added to database, pass in ids to form
    if(result.status === "success"){
        $('#genre-question').text(result.mquest);
        $('#quest_resp_movie_id').attr('value', result.id);

        $('#keyword_id1').attr('value',result.key_wrd1_id);
        $('label[for=keyword_id1]').html(result.keywrd1);
        $('#keyword_id2').attr('value',result.key_wrd2_id);
        $('label[for=keyword_id2]').html(result.keywrd2);

        $('#quest_resp_keyword_id1').attr('value',result.key_wrd1_id);
        $('#quest_resp_keyword_id2').attr('value',result.key_wrd2_id);

        $('#user-question').text(result.uquest);
        $('#userkeyword_id1').attr('value',result.key_wrd1_id);
        $('label[for=userkeyword_id1]').html(result.keywrd1);
        $('#userkeyword_id2').attr('value',result.key_wrd2_id);
        $('label[for=userkeyword_id2]').html(result.keywrd2);




        $('#quiz-form').show();
      } 
      else{
          $('#quiz-form').hide();
      } 




  });
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
  var genres_query = $("#genres");
  var sources_query = $("#sources");

  $.get("/movie.json/" + mid,function(results){
    if (results === "No movie found!" || results === "Error! Not a valid movie Identification"){
        $('#myModalLabel').html(results);

    }
    else{
      $('#myModalLabel').html(results["title"]);

      $('#rating').html("imdb rating: " + results["imdb_rating"]);
      $('#release').html("Released On: " + results["released_at"]);
      $('#runtime').html("Runtime: " + results["runtime"]);
      $('#actors').html("Actors: " + results["actors"]);

      genres_query.empty();
      for(var i=0; i < results["genres"].length; i++){
        genres_query.append("<li>" + results["genres"][i] + "</li>");
      }

      sources_query.empty();
      for (var k in results["sources"]){
        sources_query.append('<a href=' + results["sources"][k] + '><button>' + k + '</button></a>')
      }


      $('#synopsis p').html(results["plot"]);
      $('#poster img').attr('src',results["poster_url"]);
    }  
  });
}

// Event when checkbox or slider value changes
$('#check, #slider').change(sendGenre);

// update slider text value while sliding
$('#slider').on('input',function(){
  $('#range').html(this.value);
});

// Event when remove button is clicked
$('.remove').on('click',function(){
  var remove_id = {
    "movie_remove_id" : $(this).attr('id')
  };

  $.post('/remove',remove_id,function(data){
    $('#' + data).empty();

  });
});














