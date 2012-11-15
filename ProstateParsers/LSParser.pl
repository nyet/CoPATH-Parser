use strict;
use v5.10.1;

open my $LOG, ">$0.log";

open FILE, "../tests/TestCases.txt";
open TARGET, ">../tests/DesiredOutput.LSParser.csv";
my $index = 0;
my $date;
my $case_number;
my $FMP;
my $primary_tumor_grade;
my $secondary_tumor_grade;
my $total_tumor_grade;
while (my $line = <FILE>) {
	if (($line =~ /^\d+\/\d+\/\d+/)&&($date)) {
		if ($primary_tumor_grade == 0) {
			print {$LOG} "No GLEASON SCORE/tumor grade for date: $date, case_number: $case_number, FMP: $FMP\n";
		}
	}
	
	if ($line =~ /^(\d+\/\d+\/\d+)\s+(.+?)\s+(.+?)\s+/) {
		$date        = $1;
		$case_number = $2;
		$FMP         = $3;
		
		$primary_tumor_grade   = 0;
		$secondary_tumor_grade = 0;
		$total_tumor_grade     = 0;
		
		$index = 1;
	}
	
	if ($line =~ /GLEASON (SCORE|GRADE).+?(\d+)\s*\+\s*(\d+)\D+(\d+)/) { #G1+G2 SUM/G3
		$primary_tumor_grade   = $2;
		$secondary_tumor_grade = $3;
		$total_tumor_grade     = $4;
		
		print TARGET "$date,$case_number,$index,$FMP,$primary_tumor_grade,$secondary_tumor_grade,$total_tumor_grade\n";
		$index++;
	}
	if ($line =~ /GLEASON (SCORE|GRADE).+?(\d+)\D+(\d+)\s*\+\s*(\d+)/) { #SUM/G3 G1+G2
		$primary_tumor_grade   = $3;
		$secondary_tumor_grade = $4;
		$total_tumor_grade     = $2;
		
		print TARGET "$date,$case_number,$index,$FMP,$primary_tumor_grade,$secondary_tumor_grade,$total_tumor_grade\n";
		$index++;
	}
}
close FILE;
close TARGET;

close $LOG;