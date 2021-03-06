#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# enable debugging
from __future__ import with_statement
import cgi
import cgitb
cgitb.enable()

import os, sys, glob

arguments = cgi.FieldStorage()

if 'n' not in arguments.keys():
    print("Status: 303 See other")
    print("Location: https://jgross.scripts.mit.edu/world-editable-chat/?n=0")
    sys.exit(0)

print("Content-Type: text/html;charset=utf-8\n\n")
print("<!DOCTYPE html>")
print("<html>")
N = arguments['n'].value
if N not in list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    print("<body>")
    print("<div>The page you tried to access (%s) is invalid; please pass a single lower or uppercase character or a single digit as 'n' in the url parameter.</div>" % cgi.escape(N))
    print("</body>")
    print("</html>")

print("<head>")
#print("""<meta http-equiv="refresh" content="5">""")
print("<script type=text/javascript>")
print(r"""
var pretext = "";
function htmlEscape(str) { // https://stackoverflow.com/a/7124052/377022
    return str
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
function writelog(ev) {
    if (ev !== undefined) {
        window.location = "https://jgross.scripts.mit.edu/world-editable-chat/?n=%(n)s&key=" + encodeURIComponent(ev.key) + "&code=" + encodeURIComponent(ev.code) + "&pretext=" + encodeURIComponent(pretext);
    } else {
        window.location = "https://jgross.scripts.mit.edu/world-editable-chat/?n=%(n)s&pretext=" + encodeURIComponent(pretext);
    }
}
function dowritelog() { writelog(); }
var id = undefined;
function log(ev) {
    console.log([ev.key, ev.char, ev.code]);
    if (ev.code == "Enter") return writelog(ev);
    document.getElementById("typing").innerText += htmlEscape(ev.key);
    pretext += ev.key;
    clearTimeout(id);
    id = setTimeout(dowritelog, 1000);
}
function eventuallyRefresh() {
    setTimeout(function() { 
        window.location = "https://jgross.scripts.mit.edu/world-editable-chat/?n=%(n)s";
    }, 5000);
}
document.addEventListener("keypress", log, false);
document.addEventListener('keydown', function (event) { // modified from https://stackoverflow.com/a/35689827/377022
    if (event.keyCode == 8) {
        console.log('BACKSPACE was pressed');

        pretext += "^H"; // control character for backspace
        document.getElementById("typing").innerText += "^H";
        event.preventDefault();
    }
    if (event.keyCode == 46) {
        console.log('DELETE was pressed');

        event.preventDefault();
    }
});""" % {"n":cgi.escape(N)})
print("</script>")
print("""<body onload="eventuallyRefresh();">""")
print("<div>Please type something</div>")

BASE_NAME = "logs/%s" % N
ipaddress = os.environ["REMOTE_ADDR"]
MY_FILE = BASE_NAME + "." + cgi.escape(ipaddress)

good = True
if "pretext" in arguments.keys():
    if os.path.exists(MY_FILE):
        with open(MY_FILE, "r") as f:
            good = len(f.read()) < 2 ** 32
    if good:
        with open(MY_FILE, "a") as f:
            f.write(arguments["pretext"].value)
if "code" in arguments.keys():
    if arguments["code"].value == "Enter":
        if os.path.exists(MY_FILE):
            with open(MY_FILE, "r") as f:
                contents = f.read()
            with open(MY_FILE, "w") as f:
                f.write("")
            if good and os.path.exists(BASE_NAME):
                with open(BASE_NAME, "r") as f:
                    good = len(f.read()) < 2 ** 32
            if good:
                with open(BASE_NAME, "a") as f:
                    f.write("%s: %s\n" % (ipaddress, contents))
    elif "key" in arguments.keys() and arguments["key"].value:
        if good and os.path.exists(MY_FILE):
            with open(MY_FILE, "r") as f:
                good = len(f.read()) < 2 ** 32
        if good:
            with open(MY_FILE, "a") as f:
                f.write(arguments["key"].value)


def fixup(line):
    if line.startswith(ipaddress + ":"):
        return "You (%s):%s" % (ipaddress, line[len(ipaddress)+1:])
    return line

if os.path.exists(BASE_NAME):
    with open(BASE_NAME, "r") as f:
        for line in f:
            print("<div>%s</div>" % cgi.escape(fixup(line)))

for fname in sorted(glob.glob(BASE_NAME + ".*")):
    if fname != MY_FILE:
        with open(fname, "r") as f:
            print("<div>%s: %s...</div>" % (fname[len(BASE_NAME)+1:], cgi.escape(f.read())))

SO_FAR = ""
if os.path.exists(MY_FILE):
    with open(MY_FILE, "r") as f:
        SO_FAR = f.read()

print("""<div>You (%s): <span id="typing">%s</span>...</div>""" % (cgi.escape(ipaddress), cgi.escape(SO_FAR)))
if not good:
    print("<div>Error: Maximum length of chat cannot exceed 2<sup>32</sup> characters.</div>")
print("</body>")
print("</html>")
