set encoding utf8
set terminal postscript portrait size 10,7 enhanced color
set output 'temp.eps'
set size ratio 0.7
#set logscale y
unset title
unset key
set xlabel 'Ligand concentration [mM]'
set ylabel 'Normalized chemical shift [ppm]'
set mxtics
set mytics
set grid xtics ytics, mytics, mxtics
set style line 1 lc 'olive' lw 3
set style line 2 lc 'blue' lw 3
#set yrange [0:1]
#b1=0.481
#b2=0.165
#b3=0.0094
#f(x)=(1+b2/(b3-b1-b2))*exp(-b1*x-b2*x)-(b2/(b3-b1-b2))*exp(-b3*x)
#c1=0.987
#c2=2.95
#c3=0.041
#g(x)=(1+c2/(c3-c1-c2))*exp(-c1*x-c2*x)-(c2/(c3-c1-c2))*exp(-c3*x)

kd=1
dm=1
p0=0.2


f(x)=(dm*((kd+x+p0)-sqrt((kd+x+p0)**2-(4*p0*x))))/(2*p0)

#fit f(x) 'dane.dat' using 1:2 via b1,b2,b3 
plot "temp.dat" using 1:2 with points ps 1.8 pt 7