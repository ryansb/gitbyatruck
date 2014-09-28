<%inherit file="layout.mako"/>

<<<<<<< HEAD

<div class="chart"></div>
<script>
    var data = [4, 8, 15, 16, 23, 42]
    var chart = d3.select(".chart");
    var bar = chart.selectAll("div");
    var barUpdate = bar.data(data);
    var barEnter = barUpdate.enter().append("div");
    barEnter.style("width", function(d){return d* 10 + "px";});
    barEnter.text(function(d){return d;});
</script>


=======
<div class="jumbotron">
<h1>Stats for ${repo.name}</h1>
<h3>From ${repo.clone_url}</h3>
</div>
<div class="row">
<div class="col-sm-2"
<ul>
</ul>
</div>
</div>
>>>>>>> 170062d2c9403a0984e9fc6a69bf72ed0b40d9b5
