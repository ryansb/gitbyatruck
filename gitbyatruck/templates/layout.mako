<!DOCTYPE html>
<html>
<head>
<meta charset ="UTF-8">
    <title>OR Online</title>
    <meta name="keywords" content="pyramid web application" />
    <meta name="discription" content="pyramid web application" />
    <link rel="shortcut icon" href="${request.static_path('gitbyatruck:static/favicon.ico')}" />
    <link rel="stylesheet" href="${request.static_path('gitbyatruck:static/css/dist/css/bootstrap.css')}" type="text/css" media="screen" charset="utf-8" />
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
          <a class="navbar-brand" href="/">OR Online</a>
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
