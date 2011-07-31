$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

function lockForm() {
  $('#id_url').attr('disabled','disabled');
  $('.button').attr('disabled','disabled').addClass('lock-botton');
}

function unlockForm() {
  $('#id_url').removeAttr('disabled');
  $('.button').removeAttr('disabled').removeClass('lock-botton');
}

function updateDatta() {
  $.ajax({
    url: __get_status_url__,
    type: 'GET',
    context: this,
    success: function (data) {
      var msg = $('#adding').text();
      if (data.queue == 'working') {
        lockForm();
        msg = 'Adding the project to the task queue...';}
      else if (data.queue == 'done') {
        msg = 'Adding the project to the task queue completed successfully';}
      else if (data.queue == 'error') {
        msg = 'Got an error when adding the project to the task queue';
        unlockForm();}
      $('#adding').removeClass('working done error').addClass(data.queue).text(msg);

      msg = $('#cloning').text();
      if (data.cloning == 'working') {
        lockForm();
        msg = 'Cloning the project...';}
      else if (data.cloning == 'done') {
        msg = 'Cloning the project completed successfully';}
      else if (data.cloning == 'error') {
        msg = 'Got an error when cloning the project';
        unlockForm();}
      $('#cloning').removeClass('working done error').addClass(data.cloning).text(msg);

      msg = $('#parsing').text();
      if (data.parsing == 'working') {
        lockForm();
        msg = 'Parsing the source code...';}
      else if (data.parsing == 'done') {
        msg = 'Parsing the source code completed successfully';}
      else if (data.parsing == 'error') {
        msg = 'Got an error when parsing the source code';
        unlockForm();}
      $('#parsing').removeClass('working done error').addClass(data.parsing).text(msg);

      msg = $('#analyzing').text();
      if (data.analyzing == 'working') {
        lockForm();
        msg = 'Analyzing the source code...';}
      else if (data.analyzing == 'done') {
        msg = 'Analyzing the source code completed successfully';
        $('#result').addClass('view');
        unlockForm();}
      else if (data.analyzing == 'error') {
        msg = 'Got an error when analyzing the source code';
        unlockForm();}
      $('#analyzing').removeClass('working done error').addClass(data.analyzing).text(msg); 
    }
  });
}

$(function(){
  $('#dialogue form').submit(function() {
    $.ajax({
        url: __get_create_url__,
        type: 'POST',
        data: $(this).serialize(),
        context: this,
        success: function (data) {
          if (data.status == 'ok') {
            $(this).parent().removeClass('not-valid');
            lockForm();
            $('#info').text("You'll have access to the results within 30 days");
            $('#result').removeClass('view');
            $('#result a').attr('href', data.url);
          }
          else {
            $(this).parent().addClass('not-valid');
            $('#info').text(data.error);
            unlockForm();
          }
        }
    });
    return false;
  });
  
  $('#id_url').focus(function() {
    $('.dialogue').removeClass('not-valid');
    $('#info').text("You'll have access to the results within 30 days");
  });
  
  var timeout = 1000;
  updateDatta();
  setInterval(updateDatta, timeout);
});
