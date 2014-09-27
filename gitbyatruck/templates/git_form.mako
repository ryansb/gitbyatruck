<%inherit file="layout.mako"/>

<form class="form-horizontal" role="form" id="git_repo" method="post">
  <div class="form-group">
    <label for="name" class="col-sm-2 control-label">Repo Name</label>
    <div class="col-sm-10">
      <input type="text" class="form-control" id="name" placeholder="Enter Name of Repo..">
    </div>
  </div>
  <div class="form-group">
    <label for="clone_url" class="col-sm-2 control-label">Clone URL</label>
    <div class="col-sm-10">
      <input type="text" class="form-control" id="clone_url" placeholder="Enter Clone URL ...">
    </div>
  </div>
  <div class="form-group">
    <div class="col-sm-offset-2 col-sm-10">
      <input type="submit" class="btn btn-default" name="submit-btn">
    </div>
  </div>
</form>

<script type="text/javascript">
    $("#git_repo").submit(function(event)){

    /* stop form from submitting normally */
        event.preventDefault();

    /*get some values from elements on page */
        var $form = $(this),
            url = $form.attr('action');

    /* send the data using post request */
        var posting = $.post(url, {name: $('#name').val(), clone_url: $('#clone_url').val()});
        
    /* alerts the results */
        posting.done(function(data)){
            alert('success');
        };
    };
</script>
