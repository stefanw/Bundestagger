function UpdateTableHeaders() {
     $(".sticky-header").each(function() {
         var scrollTop = $(window).scrollTop();
         var offset = $(this).offset();
         var id = $(this).attr("id");
         var clone = $("#"+id+"_clone");
         var state = clone.css("display");
         var coverHeight = $("#"+id+"_content").height();
         if (state != "block" && (scrollTop > offset.top && scrollTop < offset.top+coverHeight)) {
           if(clone.length == 0){
             clone = $(this).clone().attr("id", id+"_clone").css({"top": "0px", "position": "fixed", "left": offset.left, "width":$(this).width()+"px"}).addClass("sticky-header-clone").insertAfter(this);
             activate_autocomplete();
           }
           clone.show();
         }
         else if(state == "block" && (scrollTop < offset.top || scrollTop >= offset.top+coverHeight)){
           clone.hide();
         }
     });
}

var annotation_objects = {};

function Annotations(id){
    this.id = id;
    this.text_div = $("#annotationtext_"+id);
    this.text = this.text_div.text().replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
    this.original_html = this.text_div.html();
    this.annotation_div = $("#annotations-"+id);
    this.insert_count = 0;
    this.annotations = {};
    this.selectable = false;
}

Annotations.prototype = {
    buildTextTree : function(){
      insertAt = function(str, pos, insert){
        return str.substring(0,pos)+insert+str.substring(pos,str.length);
      };
      var all_html = this.text_div.html();
      // This is a hack
      all_html = all_html.replace(/&lt;/g, "\x02").replace(/&gt;/g, "\x03").replace(/&amp;/g, "\x04").replace(/&quot;/g, "\x05").replace(/&#39;/g, "\x06");
      var new_html = all_html;
      var rest_html = all_html;
      var textCursor = -1;
      var htmlCursor = 0;
      var htmlOffset = 0;
      var opened = [];
      var reopen = [];
      var footnoteCount = 0;
      next = this.getNextStartOrEnd(textCursor);
      if (next == -1){return new_html;}
      while (new_html.charAt(htmlCursor) == "<"){
        rest_html = new_html.substring(htmlCursor, new_html.length);
        var endOfTag = rest_html.indexOf(">")+1;
        rest_html = new_html.substring(endOfTag, new_html.length);
        htmlCursor += endOfTag;
        htmlOffset += endOfTag;
      }
      while (true){
        var ends = this.getOrderedEndsAt(textCursor);
        var reopen = [];
        for(var i=0;i<ends.length;i++){
          while(opened.length > 0 && opened[opened.length-1] != ends[i]){
            reopen.push(opened[opened.length-1]);
            new_html = insertAt(new_html, htmlCursor, this.annotations[opened[opened.length-1]].end_html);
            htmlCursor += this.annotations[opened[opened.length-1]].end_html.length;
            htmlOffset += this.annotations[opened[opened.length-1]].end_html.length;
            opened = this.removeLast(opened);
          }
          new_html = insertAt(new_html, htmlCursor, this.annotations[ends[i]].end_html);
          htmlCursor += this.annotations[ends[i]].end_html.length;
          htmlOffset += this.annotations[ends[i]].end_html.length;
          opened = this.removeLast(opened);
        }
        if(new_html.charAt(htmlCursor) == "<"){
          for(var i=opened.length-1;i>=0;i--){
            new_html = insertAt(new_html, htmlCursor, this.annotations[opened[i]].end_html);
            htmlCursor += this.annotations[opened[i]].end_html.length;
            htmlOffset += this.annotations[opened[i]].end_html.length;
            reopen.push(opened[i]);            
          }
          opened = [];
        }
        while (new_html.charAt(htmlCursor) == "<"){
          rest_html = new_html.substring(htmlCursor, new_html.length);
          var endOfTag = rest_html.indexOf(">")+1;
          rest_html = rest_html.substring(endOfTag, new_html.length);
          htmlCursor += endOfTag;
          htmlOffset += endOfTag;
        }
        if(reopen.length > 0) {
          for(var j = reopen.length-1; j >= 0; j--){
            new_html = insertAt(new_html, htmlCursor, this.annotations[reopen[j]].start_html);
            htmlCursor += this.annotations[reopen[j]].start_html.length;
            htmlOffset += this.annotations[reopen[j]].start_html.length;
            opened.push(reopen[j]);
          }
        }
        var starts = this.getOrderedStartsAt(textCursor);
        for (var i = 0; i < starts.length; i++){
          new_html = insertAt(new_html, htmlCursor, this.annotations[starts[i]].start_html);
          htmlCursor += this.annotations[starts[i]].start_html.length;
          htmlOffset += this.annotations[starts[i]].start_html.length;
          if (this.annotations[starts[i]].start != this.annotations[starts[i]].end){
            opened.push(starts[i]);
          } else {
            footnoteCount += 1;
            new_html = insertAt(new_html, htmlCursor, String(footnoteCount));
            htmlCursor += String(footnoteCount).length;
            htmlOffset += String(footnoteCount).length;
            new_html = insertAt(new_html, htmlCursor, this.annotations[starts[i]].end_html);
            htmlCursor += this.annotations[starts[i]].end_html.length;
            htmlOffset += this.annotations[starts[i]].end_html.length;
            $("#annotation-"+starts[i]).hide();
            $("#footnotelist-"+this.id).append("<li>"+$("#annotation-"+starts[i]+" .content").html()+"</li>");
          }
        }
        var next = this.getNextStartOrEnd(textCursor);
        if (next == -1) {
            break;
        }
        rest_html = new_html.substring(htmlCursor, new_html.length);
        var nextHtml = rest_html.indexOf("<");
        if(nextHtml != -1 && next + htmlOffset <= htmlCursor + nextHtml){
          textCursor = next;
          htmlCursor = next + htmlOffset;
        } else {
          htmlCursor = htmlCursor + nextHtml;
          textCursor = htmlCursor - htmlOffset;
        }
      }
      // Revert hack
//      new_html = new_html.replace(/\x02/g,"&lt;").replace(/\x03/g,"&gt;").replace(/\x04/g, "&amp;").replace(/g\x05/g, "&quot;").replace(/g\x06/g, "&#39;");
      return new_html;
    },
    
    insertQuotes: function(){
      if (this.annotation_count>0){
        this.text_div.html(this.original_html);
        this.text_div.html(this.buildTextTree());
        $("#annotationtoolbox-"+this.id).show();
        var total_height = this.text_div.height() + this.text_div.nextAll(".eventlist").height();
        $("#annotations-"+this.id).css({"height": total_height+"px"});
        this.setupQuotes();
        this.repositionAnnotation();
      }
    },
    
    importQuotes: function(){
        var annotation_divs = $("#annotations-"+this.id+" .semannotation");
        this.annotation_count = annotation_divs.length;
        for (var j=0; j < annotation_divs.length; j++){
            var element = annotation_divs[j];
            var annotation = {};
            annotation.counter = j;
            annotation.id = parseInt($(element).attr("id").split("-")[1]);
            var classes = $(element).find("q").hide().attr("class");
            annotation.color = $(element).css("border-left-color");
            annotation.defaultColor = "inherit";
            classes = classes.split(" ");
            for(var i = 0; i < classes.length; i++){
                var cls = classes[i].split("_");
                if (cls.length == 2 && cls[0]=="start"){
                    annotation.start = parseInt(cls[1]);
                }
                if (cls.length == 2 && cls[0]=="end"){
                    annotation.end = parseInt(cls[1]);
                }
            }
            if (annotation.end == undefined){
                annotation.end = annotation.start;
            }
            if(annotation.end == annotation.start){
              annotation.start_html = '<sup class="annotation annotation_'+annotation.id+'">';
              annotation.end_html = "</sup>";
            }else {
              annotation.start_html = '<span class="annotation annotation_'+annotation.id+'">';
              annotation.end_html = "</span>";              
            }
            annotation.content = $(element).find(".content").html();
            this.annotations[annotation.id] = annotation;
        }
    },

    sortByEnd: function(a,b){
        if (a != -1 && b != -1){
            var diff = this.annotations[a].end - this.annotations[b].end;
            if (diff == 0){
              diff = this.annotations[b].start - this.annotations[a].start;
              if(diff == 0){
                return a - b;
              }
              return diff;
            }
            return diff;                
        }
        return a - b;
    },
    
    getOrderedEndsAt: function(index){
        var result = [];
        for(var aid in this.annotations){
            if(Math.min(this.text.length, this.annotations[aid].end) == index){
                result.push(parseInt(aid));
            }
        }
        var that = this;
        result.sort(function(a,b){return that.sortByEnd.apply(that,[a,b]);});
        return result;
    },
    getOrderedStartsAt: function(index){
        var result = [];
        for(var aid in this.annotations){
            if(Math.max(0, this.annotations[aid].start) == index){
                result.push(parseInt(aid));
            }
        }
        var that = this;
        result.sort(function(a,b){return that.sortByEnd.apply(that,[a,b]);});
        result.reverse();
        return result;
    },
        
    getNextStartOrEnd: function(textIndex){
        result = [];
        for(var aid in this.annotations){
            if(Math.max(0, this.annotations[aid].start) > textIndex){
                result.push(Math.max(0, this.annotations[aid].start));
            }
            if(Math.min(this.text.length,this.annotations[aid].end) > textIndex){
                result.push(Math.min(this.text.length, this.annotations[aid].end));
            }
        }
        if (result.length == 0){
            return -1;
        }
        sort = function(a,b){
            return a - b;
        };
        result.sort(sort);
        return result[0];
    },
        
    removeLast: function(newar){
        return newar.slice(0,newar.length-1);
    },
        
    repositionAnnotation : function(){
      var relOffset = 0;
      var leftOffset = 0;
      var offsetMap = {};
      for (var aid in this.annotations){
        var annotop = $(".annotation_"+aid).offset().top;
        var selftop = $("#annotation-"+aid).offset().top;
        if(Math.abs(annotop - selftop) > 200){
          relOffset = Math.abs(annotop - selftop);
          if (typeof offsetMap[annotop] === "undefined"){
            offsetMap[annotop] = 0;
          } else {offsetMap[annotop] = offsetMap[annotop]+1;}
        }
        if(annotop - selftop < -300){
          leftOffset = 100;
        }
        $("#annotation-"+aid).css({"top": relOffset+offsetMap[annotop]*20, "left": leftOffset+offsetMap[annotop]*20});
        leftOffset = 0;
      }
    },

    mark_quotes: function(cls){
        var color = this.getColorById(cls.split("-")[1]);
        color = this.getColorString(color);
        $("."+cls).css({"background": color});
//        $("."+cls).children().css({"background": color});
    },
    
    clear_quotes: function(cls){
        $("."+cls).css({"background": "#fff "});
//        $("."+cls).children().css({"background": "#fff "});
    },
    
    mark_quote: function(aid){
        $(".annotation_"+aid).css({"background": this.annotations[aid].color});
//        $(".annotation_"+aid).children().css({"background": this.annotations[aid].color});
    },
    
    clear_quote: function(aid){
        $(".annotation_"+aid).css({"background": this.annotations[aid].defaultColor });
//        $(".annotation_"+aid).children().css({"background": this.annotations[aid].defaultColor });
    },
    
    setupQuotes: function(){
        var obj = this;
        $(".annotationfor-"+this.id).mouseover(function(){
          var o = obj;
          var aid = $(this).attr("id").split("-")[1];
          o.mark_quote(aid);
        });
        $(".annotationfor-"+this.id).mouseout(function(){
          var o = obj;
          var aid = $(this).attr("id").split("-")[1];
          o.clear_quote(aid);
        });
/*        $(".annotation").mouseover(function(){
            obj.callFunctionForAnnotation.apply(obj,[this, obj.mark_quotes]);
        });
        $(".annotation").mouseout(function(){
            obj.callFunctionForAnnotation.apply(obj,[this, obj.clear_quotes]);
        });*/
    },
    
    getColorRGBA: function(hex, alpha){
      if(hex.indexOf("rgb")!=-1){
        hex = hex.substring(hex.indexOf("(")+1,hex.indexOf(")")).split(",");
        var r = parseInt(hex[0]);
        var g = parseInt(hex[1]);
        var b = parseInt(hex[2]);
      }
      else{
        hex = (hex.charAt(0)=="#") ? hex.substring(1,hex.length):hex;
        if (hex.length == 6){
          var r = parseInt(hex.substring(0,2), 16);
          var g = parseInt(hex.substring(2,4), 16);
          var b = parseInt(hex.substring(4,6), 16);
        }else{
          var r = parseInt(hex.substring(0,1) + hex.substring(0,1), 16);
          var g = parseInt(hex.substring(1,2) + hex.substring(1,2), 16);
          var b = parseInt(hex.substring(2,3) + hex.substring(2,3), 16);
        }
      }
      return "rgba("+r+","+g+","+b+","+alpha+")";
    },
    
    getColorById : function(aid){
        var q = parseInt(this.annotations[aid].counter);
        q = q / this.annotation_count;
        return [255 * q, 255 * (1-q), 128];
    },
    
    getColorString : function(array){
        return "rgba("+Math.round(array[0])+","+Math.round(array[1])+","+Math.round(array[2])+",0.5)";
    },
    
    callFunctionForAnnotation : function(obj, func){
        var classes = $(obj).attr("class").split(" ");
        for(var i=0;i<classes.length;i++){
            if (classes[i].match(/annotation_[0-9]+/)){
                func.apply(this, [classes[i]]);
                return;
            }
        }
    },
    
    toggleSelectView : function(){
        if(this.selectable){
            this.text_div.show();
            this.selectView.hide();
            $("#selectionhint-"+this.id).css("color", "#000");
        }
        else{
            if(this.selectView == undefined){
                var ta = document.createElement("textarea");
                ta.setAttribute("class", "selectableText");
                ta.setAttribute("id", "selectableText_"+this.id);
                ta.setAttribute("style", "display:none");
                ta.appendChild(document.createTextNode(this.text));
                this.text_div.after(ta);
                this.selectView = $("#selectableText_"+this.id);
                this.selectView.height(this.text_div.height());
                var that = this;
                if(!(/webkit/i).test(navigator.userAgent)){
                  this.selectView.attr("readonly", "true");
                }
                this.selectView.select(function(e){
                  that.updateSelectionInputs(e);
                });
                this.selectView.mouseup(function(e){
                 that.updateSelectionInputs(e);
                });
                if((/webkit/i).test(navigator.userAgent)){
                  this.selectView.keydown(function(e){
                    if(!(e.keyCode==37 || e.keyCode==38 || e.keyCode==39 || e.keyCode==40 || e.KeyCode == 16 || e.keyCode==9)){
                      e.preventDefault();
                    }
                  });
                }
                this.selectView.keyup(function(e){
                  that.updateSelectionInputs(e);
                });
              }
          this.text_div.hide();
          this.selectView.show();
          this.selectView.focus();
          }
      this.selectable = !this.selectable;
    },
    updateSelectionInputs : function(e){
      var selStart = null;
      var selEnd = null;
      if(e.target){
        if(typeof(e.target.selectionStart) == "number"){
          selStart = e.target.selectionStart;
        }
        if(typeof(e.target.selectionEnd) == "number"){
          selEnd = e.target.selectionEnd;
        }
      }
//      
      if(selStart !== null){
        $("#selection_start-"+this.id).val(selStart);
      }
      if(selEnd !== null){
       $("#selection_end-"+this.id).val(selEnd); 
      }
      if(selEnd !== null && selStart !==null){
/*        if(selEnd === selStart){
          var selected_text = this.text.substring(selStart-12, selStart)+"<sup>[1]</sup>"+this.text.substring(selEnd, selEnd+12);
          $("#selectionhint-"+this.id).html('Fußnote bei "[&hellip;]'+selected_text+'[&hellip;]"');
        }*/
        if(selEnd !== selStart){
          var selected_text = this.text.substring(selStart, selEnd);
          if(selected_text.length > 40){
            selected_text = this.text.substring(selStart, selStart+20)+"[&hellip;]"+this.text.substring(selEnd-20, selEnd);
          }
          $("#selectionhint-"+this.id).html('Markierung: "'+selected_text+'"');
          $("#selectionhint-"+this.id).css("color", "#0a0");
        }
        else{
          $("#selectionhint-"+this.id).html('Keine Markierung!');
          $("#selectionhint-"+this.id).css("color", "#a00");
        }
      }
      else{
        $("#selectionhint-"+this.id).css("color", "#a00");
      }
    },
    updateDefaultAnnotationColor : function(color){
      for(var aid in this.annotations){
        if(color == "self"){this.annotations[aid].defaultColor = this.annotations[aid].color;}
        else{this.annotations[aid].defaultColor = color;}
        if(color != "inherit"){
          $(".annotation_"+aid).css({"background": this.getColorRGBA(this.annotations[aid].defaultColor,0.5)});  
        } else{
          $(".annotation_"+aid).css({"background": this.annotations[aid].defaultColor});   
        }
      }
    }
};

activate_autocomplete = function(sel){
  if (!sel){
    sel = $(".autocompleteme");
  } else{
    sel = $("#"+sel);
  }
  sel.autocomplete("/tag/autocomplete/",{"width": 150, "max": 10, "multiple": true, "multipleSeparator": ",", "highlight": false, "scroll": true, "scrollHeight": 300, "matchContains": false, "autoFill": true});
};

newAnnotationCallback = function(data, id){
  function getStartEnd(className){
    var classes = className.split(" ");
    var ret = [null, null];
    for(var i = 0; i < classes.length; i++){
        var cls = classes[i].split("_");
        if (cls.length == 2 && cls[0]=="start"){
            ret[0] = parseInt(cls[1]);
        }
        if (cls.length == 2 && cls[0]=="end"){
            ret[1] = parseInt(cls[1]);
        }
    }
    return ret;
  }
  var className = $(data).find("q").attr("class");
  var myStartEnd = getStartEnd(className);  
  var found = false;
  $("#annotations-"+id+" .semannotation").each(function(i, el){
    if (found){return;}
    var className = $(el).find("q").attr("class");
    var startEnd = getStartEnd(className);
    if(myStartEnd[0] < startEnd[0] || (myStartEnd[0] == startEnd[0] && myStartEnd[1] < startEnd[1])){
      $(el).before(data);
      found=true;
    }
  });
  if(!found){
    $("#annotations-"+id).append(data);
  }
  annotation_objects[id].importQuotes();
  annotation_objects[id].insertQuotes();
};

newTagCallback = function(data, id){
  $(".speechtags-"+id).append(data);
  $(".speech-tags-" + id + "-container").hide();
};


$(function(){
//    $(".annotationform").hide();
    if($("#user-message").length>0){
      $("#user-message").hide().addClass("hover-message").show("normal");
      window.setTimeout(function(){$("#user-message").hide("normal");}, 5000);
    }
    $(".annotation_content").each(function(){
//            $(this).hide();
        var annoid = $(this).attr("id").split("-")[1];
        annotation_objects[annoid] = new Annotations(annoid);
    });
    for(var a in annotation_objects){
        annotation_objects[a].importQuotes();
        annotation_objects[a].insertQuotes();
    }
    $(".editform-link").click(function(e){
      e.preventDefault();
      var annoid = $(this).attr("id").split("-")[1];
      $("#editform-"+annoid).toggle();
      if($("#editform-"+annoid).css("display")=="block"){
        $(this).text("Abbrechen");
        $("#selectable-"+annoid).hide();
        $("#annotationtoolbox-"+annoid).hide();
        $("#annotations-"+annoid).hide();
      } else{
        $(this).text("Korrigieren");
        $("#selectable-"+annoid).show();
        if(annotation_objects[annoid].annotation_count >0){
          $("#annotationtoolbox-"+annoid).show();
        }
        $("#annotations-"+annoid).show();
      }
    });
    $(".annotationform-link").click(function(e){
      e.preventDefault();
      var annoid = $(this).attr("id").split("-")[1];
      annotation_objects[annoid].toggleSelectView();
      if($("#annotations-"+annoid).css("display")=="none"){
        $("#annotationform-"+annoid).hide();
        $("#annotations-"+annoid).show();
        $(this).text("Annotieren");
        $("#annotationrealform-"+annoid)[0].reset();
        $("#editable-"+annoid).show();
        if(annotation_objects[annoid].annotation_count >0){
          $("#annotationtoolbox-"+annoid).show();
        }
      } else{
        $(this).text("Abbrechen");
        $("#annotationform-"+annoid).show();
        $("#annotations-"+annoid).hide();
        if(!$("#annotationcolor-"+annoid).hasClass("colorpicking")){
          $("#annotationcolor-"+annoid).colorPicker();
        }
        $("#editable-"+annoid).hide();
        $("#annotationtoolbox-"+annoid).hide();
      }
    });
  $(".markall").click(function(e){
    var aid = $(this).attr("id").split("-")[1];
    if($(this).attr('checked')){
      annotation_objects[aid].updateDefaultAnnotationColor("self");
    } else{
      annotation_objects[aid].updateDefaultAnnotationColor("inherit");
    }
  });
  $(".addtag-form").submit(function(e){
    e.preventDefault();
    var id = $(this).attr("id").split("-")[1];
    var data = $(this).serializeArray();
    $.post($(this).attr("action"), data, function(data){var myid=id; newTagCallback(data, myid);});
  });
  $(".annotationrealform").submit(function(e){
    e.preventDefault();
    var id = $(this).attr("id").split("-")[1];
    if($("#selection_start-"+id).val()=="" || $("#selection_end-"+id).val()=="" || $("#selection_start-"+id).val()==$("#selection_end-"+id).val()){
      alert("Bitte markiere einen Textabschnitt.");
      return false;
    }
    var data = $(this).serializeArray();
    $.post($(this).attr("action"), data, function(data){var myid=id; newAnnotationCallback(data, myid);});
    $("#selectable-"+id).click();
    return false;
  });
  $(".reallydelete").live("submit", function(e){
    return confirm('Wirklich löschen?');
  });
  $(".annotationflagselect").change(function(e){
    var id = $(this).parents("form").attr("id").split("-")[1];
    var val = parseInt($(this).val());
    var color = null;
    switch(val){
      case 0: // Erklärung
        color = "#99ccff"; break;
      case 1: // Quelle?
        color = "#00ffff"; break;
      case 2: // Quelle gefunden
        color = "#00ccff"; break;
      case 3: // Querverweis
        color = "#99cc00"; break;
      case 4: // wichtig!
        color = "#ffff00"; break;
      case 5: // Faktisch falsch!
        color = "#ff0000"; break;
      case 6: // Formatierung!
        color = "#ff00ff"; break;
      case 7: // Kommentar
        color = "#c0c0c0"; break;
      default:
        color = null;
    }
    if(color != null){
      $("#color_value").val(color);
      $("#annotationcolor-"+id).val(color);
      $("div.color_picker").css("background-color", color); 
    }
  });
  if ($(".sticky-header").length>0){
    UpdateTableHeaders();
    $(window).scroll(UpdateTableHeaders);    
  }
  $(".toggle").live("click", function(e){
     e.preventDefault();
     var id = $(this).attr("id");
     if (id == ""){
       var url = $(this).attr("href");
       var sel = $("."+url.substring(1,url.length)+"-container");
     } else {var sel = $("#"+id+"-container");}
     sel.toggle();
  });
  $(".toggle_webtv").live("click", function(e){
     e.preventDefault();
     var id = $(this).attr("id");
     if (id == ""){
       var url = $(this).attr("href");
       var sel = $("."+url.substring(1,url.length)+"-container");
     } else {var sel = $("#"+id+"-container");}
     var state = sel.css("display");
     $(".webtv_div").hide();
     if (state == "none"){
       sel.show();
     }
  });
  
  $(".hide").live("click", function(e){
     e.preventDefault();
     var id = $(this).attr("id");
     if (id == ""){
       var url = $(this).attr("href");
       var sel = $("."+url.substring(1,url.length)+"-container");
     } else {var sel = $("#"+id+"-container");}
     var css = sel.css("visibility");
     if (css == "visible"){
       $(this).text("anzeigen");
       sel.css({"visibility":"hidden", "height":"0px"});
     } else{
       $(this).text("verstecken");
       sel.css({"visibility":"visible", "height":"auto"});
    }
  });
  $(".toggle-with-event").live("click", function(e){
     var id = $(this).attr("id");
     if (id == ""){
       var url = $(this).attr("href");
       var sel = $("."+url.substring(1,url.length)+"-container");
     } else {var sel = $("#"+id+"-container");}
     sel.toggle();
  });
  $('a[rel*="external"], a[rel*="license"]').click(function(e){
     e.preventDefault();
     window.open($(this).attr("href"));
  });
  activate_autocomplete();
});