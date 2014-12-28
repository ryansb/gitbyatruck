<%inherit file="layout.mako"/>


<div class="chart"></div>
<script>
    var data = $(body).data('stats');
    var chart = d3.select(".chart");
    var bar = chart.selectAll("div");
    var barUpdate = bar.data(data);
    var barEnter = barUpdate.enter().append("div");
    barEnter.style("width", function(d){return d* 10 + "px";});
    barEnter.text(function(d){return d;});
</script>

<div class="jumbotron">
<h1>Stats for ${repo.name}</h1>
<h3>From ${repo.clone_url}</h3>
</div>
${stats}
<div class="row">
<div class="col-sm-2"
<ul>
</ul>
</div>
</div>
