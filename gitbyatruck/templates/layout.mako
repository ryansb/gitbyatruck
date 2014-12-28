<!DOCTYPE html>
<html>
<head>
<meta charset ="UTF-8">
    <title>Git by a Truck</title>
    <meta name="keywords" content="pyramid web application" />
    <meta name="discription" content="pyramid web application" />
    <link rel="shortcut icon" href="${request.static_path('gitbyatruck:static/favicon.ico')}" />
    <link rel="stylesheet" href="${request.static_path('gitbyatruck:static/css/bootstrap.css')}" type="text/css" media="screen" charset="utf-8" />
    <script type="text/javascript"
            src="/static/scripts/jquery-1.4.2.min.js"></script>
    <script type="text/javascript"
            src="/static/scripts/deform.js"></script>
    <script src="${request.static_path('gitbyatruck:static/js/d3.js')}" charset="utf-8"></script>
    <style>

    .chart div {
      font: 10px sans-serif;
      background-color: steelblue;
      text-align: right;
      padding: 3px;
      margin: 1px;
      color: white;
    }
    </style>
</head>
<body>
<nav class="navbar navbar-default" role="navigation">
    <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <ul class="nav nav-pills navbar-nav">
          <li>
          <a class="navbar-brand" href="/">Git by a Truck</a>
          </li>
          </ul>
        </div>
        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <ul class="nav nav-pills navbar-nav navbar-right">
          <li class="active"><a href="/git_form">Git Form</a></li>
          </ul>
        </div>
    </div>
</nav>
<div class="container">
    ${next.body()}
</div>
</body>
</html>
