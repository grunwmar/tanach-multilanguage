#!/bin/bash

if [[ "$PY_BOOK_FORMAT" == "pdf" ]]; then
    OPT_CONFIG=" --pdf-page-margin-left $PY_BOOK_MARGIN_LEFT"   
    OPT_CONFIG+=" --pdf-page-margin-top $PY_BOOK_MARGIN_TOP"
    OPT_CONFIG+=" --pdf-page-margin-bottom $PY_BOOK_MARGIN_BOTTOM"
    OPT_CONFIG+=" --pdf-page-margin-right $PY_BOOK_MARGIN_RIGHT"
fi

if [[ "$PY_BOOK_FORMAT" == "epub" ]]; then
    OPT_CONFIG=" --margin-left $PY_BOOK_MARGIN_LEFT"
    OPT_CONFIG+=" --margin-top $PY_BOOK_MARGIN_TOP"
    OPT_CONFIG+=" --margin-bottom $PY_BOOK_MARGIN_BOTTOM"
    OPT_CONFIG+=" --margin-right $PY_BOOK_MARGIN_RIGHT"
    OPT_CONFIG+=" --embed-all-fonts"
fi

OPTIONS=" $OPT_CONFIG"
OPTIONS+=" --disable-font-rescaling" 
OPTIONS+=" --base-font-size $PY_BOOK_FONT_SIZE" 
OPTIONS+=" --level1-toc "//h:h2"" 
OPTIONS+=" --level2-toc "//h:h3"" 
OPTIONS+=" --level3-toc "//h:h4"" 
OPTIONS+=" --page-breaks-before "//h:hr"" 
OPTIONS+=" --title "$PY_BOOK_TITLE"" 

ebook-convert "$PY_BOOK_TMPFILE" "out/$PY_BOOK_FILENAME.$PY_BOOK_FORMAT" $OPTIONS       