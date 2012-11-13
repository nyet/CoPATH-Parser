#!/bin/bash
#
#
#   CaseParser
#   Copyright (C) 2012 Thorsten Alteholz
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# usage: CaseParser <infile>
# output will be sent to <stdout>

INFILE=$1
if [ "x$INFILE" == "x" ]; then
  echo "usage: CaseParser <infile>"
  exit 1
fi

TMP1=parsetmp1.$$
# just to be sure
rm -f $TMP1

# remove whitespace, remove words
# change " + " -> "+"
for f in `cat $INFILE`; do echo $f|grep "[0-9]\|+\|-\|=" >> $TMP1; done

# handle different format of grades
# change " + " -> "+"
#        " = " -> "="
#        " ["  -> "="
#        " ("  -> "="
#        ")"   -> ""
#        "("   -> ""
#        "]"   -> ""
#        "["   -> ""
#        "."   -> ""
declare -a DATA=(\
	`cat $TMP1|\
	tr '\n' ' '|\
	sed "s/ \[/=/g;s/ (/=/g"|\
	sed "s/ + /+/g;s/ = /=/g"|\
	tr -d "()[]."\
	`)
no=${#DATA[@]}

echo "INFO: Number of elements: $no"

i=0;
while [ $i -lt $no ]; do
  DATE=${DATA[$i]}
  CASE=${DATA[$i+1]}
  FMP=${DATA[$i+2]}
  # $NOM is either a+b=c or c=a+b, = might be -
  NOM=`echo ${DATA[$i+3]}|tr '-' '='`
  BLOCK=1
  i=$[i+4]

  # we have an expression on each side of the "="
  exp1=`echo $NOM|awk -F"=" '{printf("%s",$1)}'`
  exp2=`echo $NOM|awk -F"=" '{printf("%s",$2)}'`
  if [[ "$exp1" =~ [+] ]]; then
    # expression 1 is the one with both grades
    primary=`echo $exp1|awk -F"+" '{printf("%s",$1)}'`
    secondary=`echo $exp1|awk -F"+" '{printf("%s",$2)}'`
  else
    # expression 2 is the one with both grades
    primary=`echo $exp2|awk -F"+" '{printf("%s",$1)}'`
    secondary=`echo $exp2|awk -F"+" '{printf("%s",$2)}'`
  fi
  sum=$[primary+secondary]
  echo "$DATE,$CASE,$BLOCK,$FMP,$primary,$secondary,$sum"

  # we might use a while loop here
  if [[ ! "${DATA[$i]}" =~ [+/] ]]; then
     # we have a single number  (for example from WITH TERTIARY PATTERN OF 5)
     # just ignore it
     i=$[i+1]
  fi
  while [[ "${DATA[$i]}" =~ [+] ]]; do
    i=$[i+1]
    BLOCK=$[BLOCK+1]
    echo "$DATE,$CASE,$BLOCK,$FMP,$primary,$secondary,$sum"
  done
  if [[ ! "${DATA[$i]}" =~ [+/] ]]; then
     # we have a single number  (for example from WITH TERTIARY PATTERN OF 5)
     # just ignore it
     i=$[i+1]
  fi
done

rm -f $TMP1
