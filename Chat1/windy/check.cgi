#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� Windy Chat : check.cgi - 2011/09/18
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C����荞��
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

# �t�@�C��
my %log = (
	logfile => '�f�[�^�t�@�C��',
	memfile => '�ݎ��t�@�C��',
	);
foreach ( keys(%log) ) {
	if (-e $cf{$_}) {
		print "<li>$log{$_}�p�X : OK\n";
	} else {
		print "<li>$log{$_}�p�X : NG\n";
	}
	if (-r $cf{$_} && -w $cf{$_}) {
		print "<li>$log{$_}�p�[�~�b�V���� : OK\n";
	} else {
		print "<li>$log{$_}�p�[�~�b�V���� : NG\n";
	}
}

# �e���v���[�g
my @tmpl = qw|chat error form out|;
foreach (@tmpl) {
	if (-f "$cf{tmpldir}/$_.html") {
		print "<li>�e���v���[�g( $_.html ) : OK\n";
	} else {
		print "<li>�e���v���[�g( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


