#!/bin/bash

if [[ "$PY_BOOK_FORMAT" == "pdf" ]]; then
    OPT_CONFIG=" --pdf-page-margin-left $PY_BOOK_MARGIN_LEFT"   
    OPT_CONFIG+=" --pdf-page-margin-top $PY_BOOK_MARGIN_TOP"
    OPT_CONFIG+=" --pdf-page-margin-bottom $PY_BOOK_MARGIN_BOTTOM"
    OPT_CONFIG+=" --pdf-page-margin-right $PY_BOOK_MARGIN_RIGHT"
    OPT_CONFIG+=" --disable-font-rescaling"
    OPT_CONFIG+=" --pdf-hyphenate"
    OPT_CONFIG+=" --base-font-size $PY_BOOK_FONT_SIZE" 
    
fi

if [[ "$PY_BOOK_FORMAT" == "epub" ]]; then
    OPT_CONFIG+=" --embed-all-fonts"
    OPT_CONFIG+=" --base-font-size 26"
fi

OPTIONS=" $OPT_CONFIG"
OPTIONS+=" --level1-toc "//h:h2"" 
OPTIONS+=" --level2-toc "//h:h3"" 
OPTIONS+=" --level3-toc "//h:h4"" 
OPTIONS+=" --page-breaks-before "//h:hr"" 
OPTIONS+=" --title "$PY_BOOK_TITLE"" 

ebook-convert "$PY_BOOK_TMPFILE" "out/$PY_BOOK_FILENAME"_"$PY_BOOK_LANGSIGNATURE.$PY_BOOK_FORMAT" $OPTIONS       