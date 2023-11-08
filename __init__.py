from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import json

from aqt import mw
from aqt import gui_hooks

from .activity import Activity
from .config import hmd
from .links import initializeLinks

# load resources from folder
current_file_path = os.path.dirname(os.path.abspath(__file__))
svg_left_arrow_str = open(current_file_path + '/resources/left_arrow.svg', 'r').read()
svg_right_arrow_str = open(current_file_path + '/resources/right_arrow.svg', 'r').read()
js_str = open(current_file_path + '/resources/more_heatmap.js', 'rb').read().decode()
css_str = open(current_file_path + '/resources/more_heatmap.css', 'rb').read().decode()

# css that will get inserted in the HTML template
css = """<style> 

    .jumbotron {
        padding-top: 30px;
        padding-bottom: 30px;
        margin-bottom: 30px;
        color: inherit;
        background-color: #eee;
    }

    .container .more_heatmap {
        padding-right: 15px;
        padding-left: 15px;
        margin-right: auto;
        margin-left: auto;
  
    }
    
    .jumbotron p {
        margin-bottom: 15px;
        font-size: 21px;
        font-weight: 200;
    }
    
    .more_heatmap label {
        display: inline-block;
        max-width: 100%;
        margin-bottom: 5px;
        font-weight: 700;
    }       
    
    .more_heatmap p {
    margin: 0 0 10px;
    }
    
    .more_heatmap .lead {
        margin-bottom: 20px;
        font-size: 16px;
        font-weight: 300;
        line-height: 1.4;
    }
    
     .jumbotron .container {
        max-width: 100%;
    }
    
     button, select{
        font-family: inherit;
        font-size: inherit;
        line-height: inherit;
        text-transform: none;
        margin: 0;
        font: inherit;
        color: inherit;
    }
  
    .more_heatmap body {
        font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
        font-size: 14px;
        line-height: 1.42857143;
        color: #333;
        background-color: #fff;
    }

    .jumbotron h1 {
        font-size: 63px;
    }

    .jumbotron .h1 {
        color: inherit;
    }
    
    .h1, h1 {
        font-size: 36px;
    }
    
    .h1, .h2, .h3, h1, h2, h3 {
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    .h1, .h2, .h3, .h4, .h5, .h6, h1, h2, h3, h4, h5, h6 {
        font-family: inherit;
        font-weight: 500;
        line-height: 1.1;
        color: inherit;
    }
    
    .more_heatmap button {
       background-color: Transparent;
        background-repeat:no-repeat;
        border: none;
        cursor:pointer;
        overflow: hidden;
        outline:none;
    }

</style>"""

html_heatmap_template = """

    <script>
    var pybridge = function(arg){{{{
        pycmd(arg);
    }}}};
    </script>   

   <script type="text/javascript" src="http://d3js.org/d3.v3.min.js"></script>   
   <script type="text/javascript" src="http://cdn.jsdelivr.net/cal-heatmap/3.3.10/cal-heatmap.min.js"></script>   
   <link rel="stylesheet" href="http://cdn.jsdelivr.net/cal-heatmap/3.3.10/cal-heatmap.css" />   
   <script type="text/javascript">{js_bytes}</script>
   <script src="https://kit.fontawesome.com/881c8798ee.js" crossorigin="anonymous"></script>
   
   <style>{css_heatmap}</style>
   
   <style>
        #cal-heatmapzzzz .subdomain-text{{
        fill: lightgray;
        font-size: {heatmap_cell_text_size};
        font-family: {heatmap_cell_font};
        font-weight: {heatmap_cell_weight};
        }}
    </style>
   
   
   {css}
     
    <body class = "more_heatmap" style = "text-align: center;">   
    
    <div id = "container" class = "more_heatmap" style = "margin-top: {heatmap_margin_top}; zoom: {zoom}; text-align: center; display: flex; justify-content: center; align-items: center; ">
        <!-- Put this into Container to visualize border -> border-style: solid; border-color: red; border-inline-width: 5px; #999-->
        <div id="cal-heatmapzzzz" style = "margin-right: 3em; margin-top: 3em;"> 
             <div style = "margin-bottom: 20px;">    
                <button onclick="more_cal.previous();" style="margin-bottom: 5px;" class="more_heatmap"><div style="height: 10px;">{svg_left_arrow}</div></button>    
                <button onclick="more_cal.next();" style="margin-bottom: 5px;" class="more_heatmap"><div style="height: 10px;">{svg_right_arrow}</div></button>    
             </div>     
        </div>   
        <div class="jumbotron" style = " width: 450px; color: #999; background-color: #222222; border-radius: 10px;">
            <div class="container more_heatmap" style = "text-align: left;">
              <h1 class="display-4" style = 'margin-left: 20px;'>
                <label class = "more_heatmap" for="rated" > <span style = "color: white;"> Displaying </span><br> cards rated  </label><br>
                <div name = "selector" style = "border-color:#2f2f31;">
                    <select class = "selector" onchange = "onChangedSelector()" id="rated" style = "text-align: left; outline: none; margin-left: 15px; background-color: #2f2f31; border-radius: 10px;">
                    <option {select_again} style = "outline: none;" value="Again">Again</option>
                    <option {select_easy} style = "outline: none;" value="Easy">Easy</option>
                    <option {select_hard} style = "outline: none;" value="Hard">Hard</option>
                    <option {select_good} style = "outline: none;" value="Good">Good</option>
                    <option {select_added} style = "outline: none;" value="Added">Added</option>
                    </select>
                </div>
            </h1>
              <p class="more_heatmap" lead" style = "margin-left: 20px;">From two months ago. </p>
            </div>
          </div>
    </div>
    </body>
    <script type="text/javascript">
        more_cal = initMoreHeatmap({data},{legend},{offset},{heatmap_cell_size});
    </script>
"""


def checkIfSelected(name, type):
    if name != type:
        return ""
    else:
        return "Selected"


def deckbrowserRenderStats():
    """Renders the review stats inside the HTML template."""
    a = Activity(mw.col)

    # get category of cards to display (Again, Easy, ...)
    selected = hmd.getReview_type()

    # get all cards in that category
    everything = a.getEverything(selected)

    config = mw.addonManager.getConfig(__name__)

    # format the heatmap by inserting the relevant information in the HTML
    formatted_heatmap = html_heatmap_template.format(
        css=css,
        data=json.dumps(dict(everything['data'])),
        legend=json.dumps(everything['legend']),
        select_again=checkIfSelected(selected, 'Again'),
        select_easy=checkIfSelected(selected, 'Easy'),
        select_hard=checkIfSelected(selected, 'Hard'),
        select_good=checkIfSelected(selected, 'Good'),
        select_added=checkIfSelected(selected, 'Added'),
        offset=everything['offset'],
        zoom=config['zoom'],
        heatmap_cell_size=config['heatmap-cell-size'].split('px')[0],
        heatmap_cell_text_size=config['heatmap-cell-text-size'],
        heatmap_cell_font=config['heatmap-cell-font'],
        heatmap_cell_weight=config['heatmap-cell-weight'],
        heatmap_margin_top=config['heatmap-margin-top'],
        svg_left_arrow=svg_left_arrow_str,
        svg_right_arrow=svg_right_arrow_str,
        js_bytes=js_str,
        css_heatmap=css_str,
    )

    return formatted_heatmap


def displayHeatMap(deck_browser, content):
    """Display the heatmap by appending it to the stats part of the deck browser.
    This function is the main plugin function.

    It is registered by the gui-hook below, so it is called every time the decks browser is re-rendered.
    """
    content.stats += deckbrowserRenderStats()


initializeLinks()
# register plugin with hook
gui_hooks.deck_browser_will_render_content.append(displayHeatMap)
