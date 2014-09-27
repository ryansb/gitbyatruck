<!DOCTYPE html>
<html>
<head>
<meta charset ="UTF-8">
    <title>OR Online</title>
    <meta name="keywords" content="pyramid web application" />
    <meta name="discription" content="pyramid web application" />
    <link rel="shortcut icon" href="${request.static_path('gitbyatruck:static/favicon.ico')}" />
    <link rel="stylesheet" href="${request.static_path('gitbyatruck:static/css/dist/css/bootstrap.css')}" type="text/css" media="screen" charset="utf-8" />
    <!--[if lte IE 6]>
    <link rel="stylesheet" href="${request.static_path('or_online:static/ie6.css')}"  charset="utf-8" />
    <![endif]-->
</head>
<body>
<div class="container">
    <div class="jumbotron">
    stuff
    </div>
    ${next.body()}
</div>
</div>
</body>
</html>
