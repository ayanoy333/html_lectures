# ???W???[????/?????????
use strict;
my %cf;
#????????????????????????????????????????????????????????????????????
#?? Windy Chat : init.cgi - 2011/10/02
#?? Copyright(C) KentWeb
#?? http://www.kent-web.com/
#????????????????????????????????????????????????????????????????????
$cf{version} = 'WindyChat v2.1';
#????????????????????????????????????????????????????????????????????
#?? [???????]
#?? 1. ????X?N???v?g??t???[?\?t?g????B????X?N???v?g???g?p????
#??    ????????Q?????????????C????????B
#?? 2. ??u?????????T?|?[?g?f???????��??????????B
#??    ??????[????????????????????????????B
#????????????????????????????????????????????????????????????????????

#===========================================================
# ?? ??{???
#===========================================================

# ?^?C?g????
$cf{chat_title} = "Chat Room";

# ????L?L?????i????????L??????????????j
$cf{maxlog} = 30;

# ?????URL (http://????L?q???????)
$cf{homepage} = '../index.html';

# ?X?N???v?g?? (????f?????t?@?C????)
$cf{chat_cgi} = "./windy.cgi";

# ???O?t?@?C???i?t???p?X??L?q??????? / ????n???p?X?j
$cf{logfile} = "./data/log.cgi";

# ?Q????t?@?C???i?t???p?X??L?q??????? / ????n???p?X?j
$cf{memfile} = "./data/mem.cgi";

# ?e???v???[?g?f?B???N?g???y?T?[?o?p?X?z
$cf{tmpldir} = './tmpl';

# ?????F
# ?? ?????F???????O???R???}?????
$cf{colors} = [
	'#0000FF,??',
	'#DF0000,??',
	'#008040,????',
	'#800000,??',
	'#C100C1,??',
	'#FF80C0,?s???N',
	'#FF8040,?I?????W',
	'#000080,??',
	];

# ??????????b?Z?[?W
# ?? ????A???????A?????
$cf{msg_in}  = "????A??????????B";
$cf{msg_out} = "????A???????`?B";

# ????????????M???
$cf{master_name} = "MASTER";

# ???????????b?Z?[?W??F
$cf{master_color} = "#808080";

# ????????O?????|?C???^
$cf{pointer} = '??';

# ????T?C?Y?i?o?C?g?j
$cf{maxdata} = 10240;

#===========================================================
# ?? ?????
#===========================================================

# ???l????
sub init {
	return %cf;
}


1;
