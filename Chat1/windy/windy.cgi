#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� Windy Chat : windy.cgi - 2011/10/02
#�� Copyright(C) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�t�@�C���F��
require "./init.cgi";
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# ��������
if ($in{mode} eq 'regist') { &regist; }
if ($in{mode} eq 'into') { &chat_page; }
if ($in{mode} eq 'out') { &room_out; }
&form_page;

#-----------------------------------------------------------
#  �t�H�[�����
#-----------------------------------------------------------
sub form_page {
	# �N�b�L�[�擾
	my ($ck_nam,$ck_eml,$ck_col) = &get_cookie;
	$ck_col = $ck_col ne '' ? $ck_col : 0;

	my $colors;
	foreach (0 .. $#{$cf{colors}}) {
		my ($col,undef) = split(/,/, $cf{colors}->[$_]);
		if ($ck_col == $_) {
			$colors .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$colors .= qq|<input type="radio" name="color" value="$_">|;
		}
		$colors .= qq|<span style="color:$col">��</span>\n|;

		if ($_ == int(@{$cf{colors}}/2)-1) { $colors .= "<br>\n"; }
	}

	open(IN,"$cf{tmpldir}/form.html") or &error("open err: form.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!chat_title!/$cf{chat_title}/g;
	$tmpl =~ s/!chat_cgi!/$cf{chat_cgi}/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!colors!/$colors/g;
	$tmpl =~ s/!name!/$ck_nam/g;
	$tmpl =~ s/!email!/$ck_eml/g;

	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  �`���b�g���
#-----------------------------------------------------------
sub chat_page {
	if ($in{mode} eq 'into') { &regist('into'); }

	# ���O�Ȃ���IP
	if ($in{name} eq "") { $in{name} = $ENV{REMOTE_ADDR}; }

	# �ݎ�
	my ($num,$member) = &member;

	# �����F�v���_�E��
	my $op_colors;
	foreach (0 .. $#{$cf{colors}}) {
		my (undef,$nam) = split(/,/, $cf{colors}->[$_]);
		if ($in{color} == $_) {
			$op_colors .= qq|<option value="$_" selected>$nam\n|;
		} else {
			$op_colors .= qq|<option value="$_">$nam\n|;
		}
	}

	open(IN,"$cf{tmpldir}/chat.html") or &error("open err: form.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!chat_cgi!/$cf{chat_cgi}/g;
	$tmpl =~ s/!chat_title!/$cf{chat_title}/g;
	$tmpl =~ s/!name!/$in{name}/g;
	$tmpl =~ s/!email!/$in{email}/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/<!-- op_colors -->/$op_colors/g;
	$tmpl =~ s/!num!/$num/g;
	$tmpl =~ s/!member!/$member/g;
	$tmpl =~ s/!enam!/&url_encode($in{name})/eg;

	# �e���v���[�g����
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("�e���v���[�g���s���ł�");
	}

	# �w�b�_
	print "Content-type: text/html\n\n";
	print $head;

	# �������O
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while (<IN>) {
		my ($date,$name,$com,$col,undef) = split(/<>/);

		my $tmp = $loop;
		$tmp =~ s|!log:name!|<span style="color:$col">$name</span>|g;
		$tmp =~ s|!log:com!|<span style="color:$col">$com</span>|g;
		$tmp =~ s|!log:date!|$date|g;
		print $tmp;
	}
	close(IN);

	# �t�b�^
	&footer($foot);
}

#-----------------------------------------------------------
#  �L��������
#-----------------------------------------------------------
sub regist {
	# ����
	my $job = shift;

	# �R�����g�Ȃ��̓����[�h
	&chat_page if (!$job && $in{comment} eq '');

	my ($nam,$com,$eml,$col);
	if ($job eq 'into') {
		&set_cookie($in{name},$in{email},$in{color});
		$nam = $cf{master_name};
		$com = "$in{name}$cf{msg_in}";
		$col = $cf{master_color};

	} elsif ($job eq 'out') {
		$nam = $cf{master_name};
		$com = "$in{name}$cf{msg_out}";
		$col = $cf{master_color};

	} else {
		$nam = $in{email} ? qq|<a href="mailto:$in{email}">$cf{pointer}</a> <b>$in{name}</b>| : "$cf{pointer} <b>$in{name}</b>";
		$com = $in{comment};
		$eml = $in{email};
		$col = (split(/,/, $cf{colors}->[$in{color}]))[0];
	}

	# �����擾
	my ($sec,$min,$hour,$mday,$mon) = (localtime(time))[0..4];
	my $date = sprintf("%02d/%02d-%02d:%02d:%02d",$mon+1,$mday,$hour,$min,$sec);

	# �z�X�g
	my $host = &get_host;

	my ($i,@log);
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		$i++;
		push(@log,$_);
		last if ($i >= $cf{maxlog}-1);
	}
	unshift (@log,"$date<>$nam<>$com<>$col<>$host\n");
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# �L�����
	&chat_page if (!$job);
}

#-----------------------------------------------------------
#  �ގ�
#-----------------------------------------------------------
sub room_out {
	&regist('out');

	# �ݎ�
	my ($num,$member) = &member('out');

	open(IN,"$cf{tmpldir}/out.html") or &error("open err: out.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!chat_title!/$cf{chat_title}/g;
	$tmpl =~ s/!name!/$in{name}/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!num!/$num/g;
	$tmpl =~ s/!member!/$member/g;

	# �e���v���[�g����
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("�e���v���[�g���s���ł�");
	}

	# �w�b�_
	print "Content-type: text/html\n\n";
	print $head;

	# �������O
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while (<IN>) {
		my ($date,$name,$com,$col,undef) = split(/<>/);

		my $tmp = $loop;
		$tmp =~ s|!log:name!|<span style="color:$col">$name</span>|g;
		$tmp =~ s|!log:com!|<span style="color:$col">$com</span>|g;
		$tmp =~ s|!log:date!|$date|g;
		print $tmp;
	}
	close(IN);

	# �t�b�^
	&footer($foot);
}

#-----------------------------------------------------------
#  �t�H�[���f�R�[�h
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('�󗝂ł��܂���') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# �s�v�R�[�h
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]//g;

		$in{$key} = $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# ���쌠�\�L�i�폜�E���ϋ֎~�j
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:verdana,helvetica,arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">WindyChat</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  �ݎ��Ǘ�
#-----------------------------------------------------------
sub member {
	my $job = shift;

	# ����/IP�擾
	my $now = time;
	my $addr = $ENV{REMOTE_ADDR};

	my ($i,$member,$flg,@log);
	open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		my ($time,$name,$ip) = split(/<>/);

		# 60�b�ȏ㔭���̂Ȃ��҂͍폜
		if ($now - 60 > $time) {
			$flg = 1;
			next;
		}

		if ($addr eq $ip) {
			$flg = 2;

			# �ގ��ҍ폜
			if ($job eq 'out') {
				next;

			# ����/���O���X�V
			} else {
				$name = $in{name};
				$_ = "$now<>$name<>$addr<>\n";
			}
		}
		# �X�V�p�z��ɒǉ�
		push(@log,$_);

		# �Q���ҕ\���p��������쐬
		if ($i % 2) {
			$member .= "$name��";
			$i++;
		} else {
			$member .= "$name��";
			$i++;
		}
	}
	# �V�K�Q���Ғǉ�
	if (!$flg && $job ne 'out' && $in{name} ne '') {
		$flg = 3;
		push(@log,"$now<>$in{name}<>$addr<>\n");
		$member = $i % 2 ? "$member$in{name}��" : "$member$in{name}��";
	}

	# �Q���Ґ�
	my $num = @log;

	# �t�@�C���X�V
	if ($job || $flg) {
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
	}
	close(DAT);

	return ($num,$member);
}

#-----------------------------------------------------------
#  �N�b�L�[���s
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# �����t�H�[�}�b�g
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URL�G���R�[�h
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: fox_chat=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  �N�b�L�[�擾
#-----------------------------------------------------------
sub get_cookie {
	# �N�b�L�[�擾
	my $cook = $ENV{HTTP_COOKIE};

	# �Y��ID�����o��
	my %cook;
	foreach ( split(/;/, $cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URL�f�R�[�h
	my @cook;
	foreach ( split(/<>/, $cook{fox_chat}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  �z�X�g�擾
#-----------------------------------------------------------
sub get_host {
	# IP/�z�X�g�擾
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	$host ||= $addr;
	return $host;
}

#-----------------------------------------------------------
#  URL�G���R�[�h
#-----------------------------------------------------------
sub url_encode {
	my $str = shift;

	$str =~ s/([^\w ])/'%'.unpack('H2', $1)/eg;
	$str =~ tr/ /+/;
	return $str;
}

#-----------------------------------------------------------
#  �G���[���
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!error!/$err/g;

	print "Content-type: text/html\n\n";
	print $tmpl;
	exit;
}

