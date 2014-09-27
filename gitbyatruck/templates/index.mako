<%inherit file="layout.mako"/>

<div class="jumbotron">
<h1>We've crunched some serious repos, bro </h1>
</div>
<div class="row">
<div class="col-sm-2"
<ul>
% for r in repos:
    <li><a href="/repo/${r.id}">${r.name}</a> -- ${r.clone_url}</li>
% endfor
</ul>
</div>
</div>
