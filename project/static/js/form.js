var timeout = 1000,
    intervalID = false;


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

function updateStatus(data) {
  var errorMsg = 'An error occurred.'
  
  $('#adding-msg').text('');
  if (data.queue == 'working') {
    lockForm();}
  else if (data.queue == 'error') {
    $('#adding-msg').text(errorMsg);
    stopUpdateData(data);}
  $('#adding').removeClass('working done error').addClass(data.queue);

  $('#cloning-msg').text('');
  if (data.cloning == 'working') {
    lockForm();}
  else if (data.cloning == 'error') {
    $('#cloning-msg').text(errorMsg);
    stopUpdateData(data);}
  $('#cloning').removeClass('working done error').addClass(data.cloning);

  $('#parsing-msg').text('');
  if (data.parsing == 'working') {
    lockForm();}
  else if (data.parsing == 'error') {
    $('#parsing-msg').text(errorMsg);
    stopUpdateData(data);}
  $('#parsing').removeClass('working done error').addClass(data.parsing);

  $('#analyzing-msg').text('');
  if (data.analyzing == 'working') {
    lockForm();}
  else if (data.analyzing == 'done') {
    $('#result').addClass('view');
    stopUpdateData(data);}
  else if (data.analyzing == 'error') {
    $('#analyzing-msg').text(errorMsg);
    stopUpdateData(data);}
  $('#analyzing').removeClass('working done error').addClass(data.analyzing); 
}

function lockForm() {
  $('#id_url').attr('disabled','disabled');
  $('.button').attr('disabled','disabled').addClass('lock-botton');
}

function unlockForm() {
  $('#id_url').removeAttr('disabled');
  $('.button').removeAttr('disabled').removeClass('lock-botton');
}

function startUpdateData(data) {
  lockForm();
  intervalID = setInterval(function () {
    $.ajax({
      url: __get_status_url__,
      type: 'GET',
      context: this,
      success: function (data) {
        updateStatus(data);
      }
    });
  }, timeout);
}

function stopUpdateData(data) {
  if (intervalID) {
    clearInterval(intervalID);
  }
  unlockForm();
}

function registerError(msg) {
  $('#dialogue').addClass('not-valid');
  $('#error').text(msg);
}

function cancelError() {
  $('#dialogue').removeClass('not-valid');
  $('#error').text('');
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
            startUpdateData(data);
            cancelError();
            $('#result').removeClass('view');
            $('#result a').attr('href', data.url);
          }
          else {
            registerError(data.error);
            unlockForm();
          }
        }
    });
    return false;
  });
  
  $('#id_url').focus(cancelError);

  $('#example-url').click(function() {
    $('#id_url').val($(this).text());
    cancelError();
    return false;
  });

  $.ajax({
    url: __get_status_url__,
    type: 'GET',
    context: this,
    success: function (data) {
      updateStatus(data);
      if (data.queue == 'working' || data.cloning == 'working' || data.parsing == 'working' || data.analyzing == 'working') {
        startUpdateData(data);
      }
    }
  });
});
