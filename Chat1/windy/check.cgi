#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Windy Chat : check.cgi - 2011/09/18
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# ファイル
my %log = (
	logfile => 'データファイル',
	memfile => '在室ファイル',
	);
foreach ( keys(%log) ) {
	if (-e $cf{$_}) {
		print "<li>$log{$_}パス : OK\n";
	} else {
		print "<li>$log{$_}パス : NG\n";
	}
	if (-r $cf{$_} && -w $cf{$_}) {
		print "<li>$log{$_}パーミッション : OK\n";
	} else {
		print "<li>$log{$_}パーミッション : NG\n";
	}
}

# テンプレート
my @tmpl = qw|chat error form out|;
foreach (@tmpl) {
	if (-f "$cf{tmpldir}/$_.html") {
		print "<li>テンプレート( $_.html ) : OK\n";
	} else {
		print "<li>テンプレート( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


