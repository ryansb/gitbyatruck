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

<script>
$.ajax({
    type: "POST";
    url: "${request.route_url('addrepo')}",
    data: JSON.stringify({clone_url: "", name: ""}),
    contentType="application/json; charset=uft8",
    dataType: "json"
})
</script>
