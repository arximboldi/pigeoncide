#
# Compilación del latex.
#

articulo.dvi: articulo.tex
	latex \\nonstopmode\\input articulo.tex

articulo.pdf: articulo.dvi
	dvipdf articulo.dvi

pdf: articulo.pdf

cleantmp:
	rm -f *.out *.log *.toc *.idx *~ *#

cleanout:
	rm -f *.pdf *.dvi *.tar.gz

clean: cleantmp cleanout

dist: 
	tar czvf articulo.tar.gz makefile *.tex *.sty *.pdf
