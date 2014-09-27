<%inherit file="layout.mako"/>

<form action="#" method="post">
    <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
            <label class="col-sm-2 control-label">Name </label>
            <input type="text" class="form-control" name="name" placeholder="Name here...">
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
            <label class="col-sm-2 control-label"> Clone URL </label>
            <input type="text" class="form-control" name="clone_url" placeholder="Clone URL here...">
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
            <input type="submit" class="btn btn-default">
        </div>
    </div>
</form>
