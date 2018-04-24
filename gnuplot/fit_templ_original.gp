set encoding utf8
#set terminal postscript portrait size 10,7 enhanced color
#set output 'fit.eps'
set terminal png size %d,%d
set output 'fit.png'
set size ratio %f

unset title
unset key
set xlabel 'Ligand concentration [mM]'
set ylabel 'Relative chemical shift [ppm]'
set mxtics
set mytics
set grid xtics ytics, mytics, mxtics
set style line 1 lc 'olive' lw 1
set style line 2 lc 'blue' lw 1


kd=%f
dm=%f
p0=%f


f(x)=(dm*((kd+x+p0)-sqrt((kd+x+p0)**2-(4*p0*x))))/(2*p0)


plot "temp.dat" using 1:2 with points ps 1.8 pt 7,%s f(x) ls 1