#!/bin/perl


#################################################################
#pingsweep.pl					               	#
#                               				#
#Leverages the Net::Ping CPAN module                            #
#Pings each host in 192.168.16.0/23 in it's own thread 		#
#								#
#Problems:						     	#
# 1> I don't really manage the threads at all this could cause	#
#	a crash							#
# 2> Just like the bash one, the network isnt' auto-parsed	#
#################################################################


use strict;
use warnings;
use threads;
use threads::shared;
use Net::Ping;


my @ipaddresses;


for ( my $third = 16; $third <= 17; $third ++ ) {

	for ( my $forth = 0; $forth <= 255; $forth ++ ) {

		push(@ipaddresses, "192.168." . $third . "." . $forth);

	}

}

my @threadlist;

foreach (@ipaddresses) {

	my $thread = threads->new(\&pingtest, $_ );
	push(@threadlist, $thread);
	

}



foreach (@threadlist) {

	$_->join();

}


sub pingtest {

	my $ip = shift;

	my $ping = Net::Ping->new();

	if ($ping->ping($ip)) {

		print $ip . "\r\n";

	}

	$ping->close();

}

