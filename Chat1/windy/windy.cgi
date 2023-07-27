#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Windy Chat : windy.cgi - 2011/10/02
#│ Copyright(C) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定ファイル認識
require "./init.cgi";
my %cf = &init;

# データ受理
my %in = &parse_form;

# 処理分岐
if ($in{mode} eq 'regist') { &regist; }
if ($in{mode} eq 'into') { &chat_page; }
if ($in{mode} eq 'out') { &room_out; }
&form_page;

#-----------------------------------------------------------
#  フォーム画面
#-----------------------------------------------------------
sub form_page {
	# クッキー取得
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
		$colors .= qq|<span style="color:$col">■</span>\n|;

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
#  チャット画面
#-----------------------------------------------------------
sub chat_page {
	if ($in{mode} eq 'into') { &regist('into'); }

	# 名前なしはIP
	if ($in{name} eq "") { $in{name} = $ENV{REMOTE_ADDR}; }

	# 在室
	my ($num,$member) = &member;

	# 文字色プルダウン
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

	# テンプレート分割
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("テンプレートが不正です");
	}

	# ヘッダ
	print "Content-type: text/html\n\n";
	print $head;

	# 発言ログ
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

	# フッタ
	&footer($foot);
}

#-----------------------------------------------------------
#  記事書込み
#-----------------------------------------------------------
sub regist {
	# 引数
	my $job = shift;

	# コメントなしはリロード
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

	# 日時取得
	my ($sec,$min,$hour,$mday,$mon) = (localtime(time))[0..4];
	my $date = sprintf("%02d/%02d-%02d:%02d:%02d",$mon+1,$mday,$hour,$min,$sec);

	# ホスト
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

	# 記事画面
	&chat_page if (!$job);
}

#-----------------------------------------------------------
#  退室
#-----------------------------------------------------------
sub room_out {
	&regist('out');

	# 在室
	my ($num,$member) = &member('out');

	open(IN,"$cf{tmpldir}/out.html") or &error("open err: out.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!chat_title!/$cf{chat_title}/g;
	$tmpl =~ s/!name!/$in{name}/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!num!/$num/g;
	$tmpl =~ s/!member!/$member/g;

	# テンプレート分割
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("テンプレートが不正です");
	}

	# ヘッダ
	print "Content-type: text/html\n\n";
	print $head;

	# 発言ログ
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

	# フッタ
	&footer($foot);
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('受理できません') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# 不要コード
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
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
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
#  在室管理
#-----------------------------------------------------------
sub member {
	my $job = shift;

	# 時間/IP取得
	my $now = time;
	my $addr = $ENV{REMOTE_ADDR};

	my ($i,$member,$flg,@log);
	open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		my ($time,$name,$ip) = split(/<>/);

		# 60秒以上発言のない者は削除
		if ($now - 60 > $time) {
			$flg = 1;
			next;
		}

		if ($addr eq $ip) {
			$flg = 2;

			# 退室者削除
			if ($job eq 'out') {
				next;

			# 時間/名前を更新
			} else {
				$name = $in{name};
				$_ = "$now<>$name<>$addr<>\n";
			}
		}
		# 更新用配列に追加
		push(@log,$_);

		# 参加者表示用文字列を作成
		if ($i % 2) {
			$member .= "$name◇";
			$i++;
		} else {
			$member .= "$name◆";
			$i++;
		}
	}
	# 新規参加者追加
	if (!$flg && $job ne 'out' && $in{name} ne '') {
		$flg = 3;
		push(@log,"$now<>$in{name}<>$addr<>\n");
		$member = $i % 2 ? "$member$in{name}◇" : "$member$in{name}◆";
	}

	# 参加者数
	my $num = @log;

	# ファイル更新
	if ($job || $flg) {
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
	}
	close(DAT);

	return ($num,$member);
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: fox_chat=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};

	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/, $cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URLデコード
	my @cook;
	foreach ( split(/<>/, $cook{fox_chat}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  ホスト取得
#-----------------------------------------------------------
sub get_host {
	# IP/ホスト取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	$host ||= $addr;
	return $host;
}

#-----------------------------------------------------------
#  URLエンコード
#-----------------------------------------------------------
sub url_encode {
	my $str = shift;

	$str =~ s/([^\w ])/'%'.unpack('H2', $1)/eg;
	$str =~ tr/ /+/;
	return $str;
}

#-----------------------------------------------------------
#  エラー画面
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

