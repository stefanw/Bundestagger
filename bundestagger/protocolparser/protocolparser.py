#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parses Bundestag Protocols from XML from Adobe Acrobat XML Extraction"""

import re
from xml.etree import ElementTree as ET

NAME_NODES = ("_N",)
TEXT_NODES = ("_J", "_O", "_Z", "_T", "_p",)
EVENT_NODES = ("_K",)
POLL_NODES = ("_AL_Vorspann",)

IGNORE_NODES = ("TextSection", "Figure", "_AL_Namen", "_AL_Partei", "_Z_Inhalt", "_Z_Datum",
    "_Z_Sitzung", "_Z_Steno", "_Z_Bundestag","Lbl","_Z_Fussnote", "_A_NaechsteSitzung",)
    
COMMENT_KINDS = [u"Heiterkeit", u"Zurufe", u"Zuruf", u"Gegenruf", u"Beifall", u"Lachen",
        u"Unterbrechung", u"Schluss", u"Unruhe", u"Zustimmung", u"Widerspruch", 
        u"Lebhafter Beifall", u"Anhaltender Beifall", u"Lang anhaltender Beifall"]
COMMENT_KINDS.reverse()
COMMENT_KINDS = tuple(COMMENT_KINDS)

RE_ENDS_WITH_WHITESPACE = re.compile("\s$")
RE_STARTS_WITH_WHITESPACE = re.compile("^\s")

class DebateTransformer(object):
    """currently doesn't work"""
    def __init__(self):
        pass
        
    def get_times(self):
        begins = re.findall("\s?Beginn:\s*([0-9]\s*[0-9]?)\s*\.\s*([0-9]\s*[0-9]?)\s*Uhr", self.xml)
        beginn = None
        if len(begins)>1:
            print "-"*80 + "too many begins!"
        elif len(begins)==0:
            print "-"*80 + "no begin!"
        else:
            begins0 = re.sub("\s", "", begins[0][0])
            begins1 = re.sub("\s", "", begins[0][1])
            beginn = (int(begins0), int(begins1))
        ends = re.findall("\s*Schluss(?:\s*der\s*Sitzung)?:?\s*([0-9]\s*[0-9]?)\s*\.\s*([0-9]\s*[0-9]?)\s*Uhr\s*", self.xml)
        ende = None
        if len(ends)>1:
            print "-"*80 + "too many ends!"
        elif len(ends)==0:
            print "-"*80 + "no end!"
        else:
            ends0 = re.sub("\s", "", ends[0][0])
            ends1 = re.sub("\s", "", ends[0][1])
            ende = (int(ends0), int(ends1))
        return (beginn, ende)
        
class Extractor(object):
    def fix_xml_string(self, xmlstr):
        xmlstr = xmlstr.replace(''' ''', ' ') # wtf is that? It must go
        xmlstr = xmlstr.replace('''<Figure/>''', '') # no need for figures
        return xmlstr

    def get_text_from_item(self, item):
        text = item.text
        if text is None:
            text = ""
        text = text.strip()
        if item.tail is not None and len(item.tail.strip()):
            # if not RE_ENDS_WITH_WHITESPACE.search(text) and \
            #         not RE_STARTS_WITH_WHITESPACE.search(item.tail):
            text = "%s\n%s" % (text, item.tail.strip())
        return text

class TopExtractor(Extractor):
    def __init__(self):
        self.sessiontops = []
        self.current_sessiontop = None
        self.current_topspeakers = []
        self.has_toptext = False

    def fix_xml_string(self, xmlstr):
        xmlstr = re.sub('<ImageData src="[^"]+"/>', '', xmlstr)
        xmlstr = re.sub('(?m)<Figure>[^<]+</Figure>','', xmlstr)
        xmlstr = super(TopExtractor, self).fix_xml_string(xmlstr)
        return xmlstr

    def parse(self, xmlstr):
        """Returns list of Tops as dictionaries"""
        xmlstr = self.fix_xml_string(xmlstr)
        self.xmlstr = xmlstr
        self.rootelem = ET.fromstring(xmlstr)
        for section in self.rootelem.findall(".//TextSection"):
            for item in section.getiterator():
                self.parse_next(item)
        return self.sessiontops
        
    def save_current(self):
        if self.current_sessiontop is None:
            return
        self.current_sessiontop["about"] = self.current_sessiontop["about"].strip()
        self.current_sessiontop["speakers"] = self.current_topspeakers
        self.sessiontops.append(self.current_sessiontop)
        self.current_sessiontop = None
        self.current_topspeakers = []
        self.has_toptext = False

    def remove_dots(self, text):
        text = text.replace(" .", "").strip()
        if text.endswith("."):
            text = text[:-1]
        if text.endswith(":"):
            text = text[:-1]
        return text

    def parse_next(self, item, context=None):
        """<_A_TOP MCID="5">Tagesordnungspunkt 1:</_A_TOP>
        <_A_TOP_Text MCID="6">Wahl eines Stellvertreters des Präsidenten </_A_TOP_Text>
        <_A_TOP_Redner MCID="8">Präsident Dr. Norbert Lammert  . . . . . . . . . . .</_A_TOP_Redner>
        """
        text = self.get_text_from_item(item)
        if item.tag in ("_A_TOP_Text_EStrich",):
            self.has_toptext = True
            self.current_sessiontop["about"]+="\n -%s" % self.remove_dots(text)
        elif self.current_sessiontop is not None and item.tag.startswith("_A_TOP_") and "Redner" in item.tag:
            self.current_topspeakers.append(self.remove_dots(text))
        elif self.current_sessiontop is not None and item.tag != "_A_TOP" and item.tag.startswith("_A_") and not self.has_toptext:
            self.current_sessiontop["about"] += self.remove_dots(text)+'\n'
            self.has_toptext = True
        elif item.tag == "_A_TOP":
            print "start top: %s" % text
            self.save_current()
            self.current_sessiontop = {'title': self.remove_dots(text), 'about':''}
        else:
            pass
            # print "Unknown %s" % item.tag

class DebateExtractor(Extractor):
    def __init__(self):
        self.xmlstr = None
        self.rootelem = None
        self.current_speaker = None
        self.current_textparts = None
        self.current_events = None
        self.last_node = None
        self.speeches = []

    def parse(self, xmlstr):
        """Returns list of Speakers with their textparts and events for each textpart"""
        xmlstr = self.fix_xml_string(xmlstr)
        self.xmlstr = xmlstr
        self.rootelem = ET.fromstring(xmlstr)
        for section in self.rootelem.findall(".//TextSection"):
            for item in section.getiterator():
                self.parse_next(item)
        self.save_current()
        return self.speeches
    
    def save_current(self):
        if self.current_speaker is None:
            return
        self.speeches.append({"speaker":self.current_speaker,
            "textparts": self.current_textparts,
            "events": self.current_events
            })
        
    def create_event(self, text):
        """Needs extracting here, maybe something clear and sane this time"""
        return text
    
    def parse_next(self, item, context=None):
        text = self.get_text_from_item(item)
        if item.tag in IGNORE_NODES:
            return
        if item.tag.startswith(NAME_NODES):
            self.save_current()
            self.current_speaker = text
            self.current_events = []
            self.current_textparts = []
            self.last_node = "name"
        elif item.tag.startswith(EVENT_NODES):
            self.current_events[-1].append(self.create_event(text))
            self.last_node = "event"
        elif item.tag.startswith(TEXT_NODES):
            if self.last_node == "text":
                # if not RE_ENDS_WITH_WHITESPACE.search(text) and \
                #         not RE_STARTS_WITH_WHITESPACE.search(text):
                self.current_textparts[-1] += "\n%s" % text
            else:
                self.current_textparts.append(text)
                self.current_events.append([])
            self.last_node = "text"
        else:
            pass