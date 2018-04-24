set encoding utf8
#set terminal postscript portrait size 7,5 enhanced color
#set output 'fit.eps'
set terminal png size 531,310
set output 'fit.png'
set size ratio 0.583804

unset title
unset key
set xlabel 'Ligand concentration [mM]'
set ylabel 'Relative chemical shift [ppm]'
set mxtics
set mytics
set grid xtics ytics#, mytics, mxtics
set style line 1 lc 'olive' lw 1
set style line 2 lc 'blue' lw 1


kd=1868.881284
dm=12.742131
p0=0.300000


f(x)=(dm*((kd+x+p0)-sqrt((kd+x+p0)**2-(4*p0*x))))/(2*p0)


plot "temp.dat" using 1:2 with points ps 1.8 pt 7, f(x) ls 1