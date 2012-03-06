# -*- coding: latin-1 -*-

from string import *
import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs
import socket, base64
import pyDes

Request = urllib2.Request
urlopen = urllib2.urlopen

__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__language__ = __settings__.getLocalizedString

rootDir = __settings__.getAddonInfo('path')

if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')


enable_debug = True


# Set cookie file
cookiePath = xbmc.translatePath(os.path.join(cacheDir, 'cookies.lwp'))
cj = cookielib.LWPCookieJar(cookiePath)
try:
    cj.load()
except:
    cj.save()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

    #opener = urllib2.build_opener()
    #urllib2.install_opener(opener)


entitydefs = {
    'AElig':    u'\u00C6', # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1'
    'Aacute':   u'\u00C1', # latin capital letter A with acute, U+00C1 ISOlat1'
    'Acirc':    u'\u00C2', # latin capital letter A with circumflex, U+00C2 ISOlat1'
    'Agrave':   u'\u00C0', # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1'
    'Alpha':    u'\u0391', # greek capital letter alpha, U+0391'
    'Aring':    u'\u00C5', # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1'
    'Atilde':   u'\u00C3', # latin capital letter A with tilde, U+00C3 ISOlat1'
    'Auml':     u'\u00C4', # latin capital letter A with diaeresis, U+00C4 ISOlat1'
    'Beta':     u'\u0392', # greek capital letter beta, U+0392'
    'Ccedil':   u'\u00C7', # latin capital letter C with cedilla, U+00C7 ISOlat1'
    'Chi':      u'\u03A7', # greek capital letter chi, U+03A7'
    'Dagger':   u'\u2021', # double dagger, U+2021 ISOpub'
    'Delta':    u'\u0394', # greek capital letter delta, U+0394 ISOgrk3'
    'ETH':      u'\u00D0', # latin capital letter ETH, U+00D0 ISOlat1'
    'Eacute':   u'\u00C9', # latin capital letter E with acute, U+00C9 ISOlat1'
    'Ecirc':    u'\u00CA', # latin capital letter E with circumflex, U+00CA ISOlat1'
    'Egrave':   u'\u00C8', # latin capital letter E with grave, U+00C8 ISOlat1'
    'Epsilon':  u'\u0395', # grek capital letter epsilon, U+0395'
    'Eta':      u'\u0397', # greek capital letter eta, U+0397'
    'Euml':     u'\u00CB', # latin capital letter E with diaeresis, U+00CB ISOlat1'
    'Gamma':    u'\u0393', # greek capital letter gamma, U+0393 ISOgrk3'
    'Iacute':   u'\u00CD', # latin capital letter I with acute, U+00CD ISOlat1'
    'Icirc':    u'\u00CE', # latin capital letter I with circumflex, U+00CE ISOlat1'
    'Igrave':   u'\u00CC', # latin capital letter I with grave, U+00CC ISOlat1'
    'Iota':     u'\u0399', # greek capital letter iota, U+0399'
    'Iuml':     u'\u00CF', # latin capital letter I with diaeresis, U+00CF ISOlat1'
    'Kappa':    u'\u039A', # greek capital letter kappa, U+039A'
    'Lambda':   u'\u039B', # greek capital letter lambda, U+039B ISOgrk3'
    'Mu':       u'\u039C', # greek capital letter mu, U+039C'
    'Ntilde':   u'\u00D1', # latin capital letter N with tilde, U+00D1 ISOlat1'
    'Nu':       u'\u039D', # greek capital letter nu, U+039D'
    'OElig':    u'\u0152', # latin capital ligature OE, U+0152 ISOlat2'
    'Oacute':   u'\u00D3', # latin capital letter O with acute, U+00D3 ISOlat1'
    'Ocirc':    u'\u00D4', # latin capital letter O with circumflex, U+00D4 ISOlat1'
    'Ograve':   u'\u00D2', # latin capital letter O with grave, U+00D2 ISOlat1'
    'Omega':    u'\u03A9', # greek capital letter omega, U+03A9 ISOgrk3'
    'Omicron':  u'\u039F', # greek capital letter omicron, U+039F'
    'Oslash':   u'\u00D8', # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1'
    'Otilde':   u'\u00D5', # latin capital letter O with tilde, U+00D5 ISOlat1'
    'Ouml':     u'\u00D6', # latin capital letter O with diaeresis, U+00D6 ISOlat1'
    'Phi':      u'\u03A6', # greek capital letter phi, U+03A6 ISOgrk3'
    'Pi':       u'\u03A0', # greek capital letter pi, U+03A0 ISOgrk3'
    'Prime':    u'\u2033', # double prime = seconds = inches, U+2033 ISOtech'
    'Psi':      u'\u03A8', # greek capital letter psi, U+03A8 ISOgrk3'
    'Rho':      u'\u03A1', # greek capital letter rho, U+03A1'
    'Scaron':   u'\u0160', # latin capital letter S with caron, U+0160 ISOlat2'
    'Sigma':    u'\u03A3', # greek capital letter sigma, U+03A3 ISOgrk3'
    'THORN':    u'\u00DE', # latin capital letter THORN, U+00DE ISOlat1'
    'Tau':      u'\u03A4', # greek capital letter tau, U+03A4'
    'Theta':    u'\u0398', # greek capital letter theta, U+0398 ISOgrk3'
    'Uacute':   u'\u00DA', # latin capital letter U with acute, U+00DA ISOlat1'
    'Ucirc':    u'\u00DB', # latin capital letter U with circumflex, U+00DB ISOlat1'
    'Ugrave':   u'\u00D9', # latin capital letter U with grave, U+00D9 ISOlat1'
    'Upsilon':  u'\u03A5', # greek capital letter upsilon, U+03A5 ISOgrk3'
    'Uuml':     u'\u00DC', # latin capital letter U with diaeresis, U+00DC ISOlat1'
    'Xi':       u'\u039E', # greek capital letter xi, U+039E ISOgrk3'
    'Yacute':   u'\u00DD', # latin capital letter Y with acute, U+00DD ISOlat1'
    'Yuml':     u'\u0178', # latin capital letter Y with diaeresis, U+0178 ISOlat2'
    'Zeta':     u'\u0396', # greek capital letter zeta, U+0396'
    'aacute':   u'\u00E1', # latin small letter a with acute, U+00E1 ISOlat1'
    'acirc':    u'\u00E2', # latin small letter a with circumflex, U+00E2 ISOlat1'
    'acute':    u'\u00B4', # acute accent = spacing acute, U+00B4 ISOdia'
    'aelig':    u'\u00E6', # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1'
    'agrave':   u'\u00E0', # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1'
    'alefsym':  u'\u2135', # alef symbol = first transfinite cardinal, U+2135 NEW'
    'alpha':    u'\u03B1', # greek small letter alpha, U+03B1 ISOgrk3'
    'amp':      u'\u0026', # ampersand, U+0026 ISOnum'
    'and':      u'\u2227', # logical and = wedge, U+2227 ISOtech'
    'ang':      u'\u2220', # angle, U+2220 ISOamso'
    'aring':    u'\u00E5', # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1'
    'asymp':    u'\u2248', # almost equal to = asymptotic to, U+2248 ISOamsr'
    'atilde':   u'\u00E3', # latin small letter a with tilde, U+00E3 ISOlat1'
    'auml':     u'\u00E4', # latin small letter a with diaeresis, U+00E4 ISOlat1'
    'bdquo':    u'\u201E', # double low-9 quotation mark, U+201E NEW'
    'beta':     u'\u03B2', # greek small letter beta, U+03B2 ISOgrk3'
    'brvbar':   u'\u00A6', # broken bar = broken vertical bar, U+00A6 ISOnum'
    'bull':     u'\u2022', # bullet = black small circle, U+2022 ISOpub'
    'cap':      u'\u2229', # intersection = cap, U+2229 ISOtech'
    'ccedil':   u'\u00E7', # latin small letter c with cedilla, U+00E7 ISOlat1'
    'cedil':    u'\u00B8', # cedilla = spacing cedilla, U+00B8 ISOdia'
    'cent':     u'\u00A2', # cent sign, U+00A2 ISOnum'
    'chi':      u'\u03C7', # greek small letter chi, U+03C7 ISOgrk3'
    'circ':     u'\u02C6', # modifier letter circumflex accent, U+02C6 ISOpub'
    'clubs':    u'\u2663', # black club suit = shamrock, U+2663 ISOpub'
    'cong':     u'\u2245', # approximately equal to, U+2245 ISOtech'
    'copy':     u'\u00A9', # copyright sign, U+00A9 ISOnum'
    'crarr':    u'\u21B5', # downwards arrow with corner leftwards = carriage return, U+21B5 NEW'
    'cup':      u'\u222A', # union = cup, U+222A ISOtech'
    'curren':   u'\u00A4', # currency sign, U+00A4 ISOnum'
    'dArr':     u'\u21D3', # downwards double arrow, U+21D3 ISOamsa'
    'dagger':   u'\u2020', # dagger, U+2020 ISOpub'
    'darr':     u'\u2193', # downwards arrow, U+2193 ISOnum'
    'deg':      u'\u00B0', # degree sign, U+00B0 ISOnum'
    'delta':    u'\u03B4', # greek small letter delta, U+03B4 ISOgrk3'
    'diams':    u'\u2666', # black diamond suit, U+2666 ISOpub'
    'divide':   u'\u00F7', # division sign, U+00F7 ISOnum'
    'eacute':   u'\u00E9', # latin small letter e with acute, U+00E9 ISOlat1'
    'ecirc':    u'\u00EA', # latin small letter e with circumflex, U+00EA ISOlat1'
    'egrave':   u'\u00E8', # latin small letter e with grave, U+00E8 ISOlat1'
    'empty':    u'\u2205', # empty set = null set = diameter, U+2205 ISOamso'
    'emsp':     u'\u2003', # em space, U+2003 ISOpub'
    'ensp':     u'\u2002', # en space, U+2002 ISOpub'
    'epsilon':  u'\u03B5', # greek small letter epsilon, U+03B5 ISOgrk3'
    'equiv':    u'\u2261', # identical to, U+2261 ISOtech'
    'eta':      u'\u03B7', # greek small letter eta, U+03B7 ISOgrk3'
    'eth':      u'\u00F0', # latin small letter eth, U+00F0 ISOlat1'
    'euml':     u'\u00EB', # latin small letter e with diaeresis, U+00EB ISOlat1'
    'euro':     u'\u20AC', # euro sign, U+20AC NEW'
    'exist':    u'\u2203', # there exists, U+2203 ISOtech'
    'fnof':     u'\u0192', # latin small f with hook = function = florin, U+0192 ISOtech'
    'forall':   u'\u2200', # for all, U+2200 ISOtech'
    'frac12':   u'\u00BD', # vulgar fraction one half = fraction one half, U+00BD ISOnum'
    'frac14':   u'\u00BC', # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum'
    'frac34':   u'\u00BE', # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum'
    'frasl':    u'\u2044', # fraction slash, U+2044 NEW'
    'gamma':    u'\u03B3', # greek small letter gamma, U+03B3 ISOgrk3'
    'ge':       u'\u2265', # greater-than or equal to, U+2265 ISOtech'
    'gt':       u'\u003E', # greater-than sign, U+003E ISOnum'
    'hArr':     u'\u21D4', # left right double arrow, U+21D4 ISOamsa'
    'harr':     u'\u2194', # left right arrow, U+2194 ISOamsa'
    'hearts':   u'\u2665', # black heart suit = valentine, U+2665 ISOpub'
    'hellip':   u'\u2026', # horizontal ellipsis = three dot leader, U+2026 ISOpub'
    'iacute':   u'\u00ED', # latin small letter i with acute, U+00ED ISOlat1'
    'icirc':    u'\u00EE', # latin small letter i with circumflex, U+00EE ISOlat1'
    'iexcl':    u'\u00A1', # inverted exclamation mark, U+00A1 ISOnum'
    'igrave':   u'\u00EC', # latin small letter i with grave, U+00EC ISOlat1'
    'image':    u'\u2111', # blackletter capital I = imaginary part, U+2111 ISOamso'
    'infin':    u'\u221E', # infinity, U+221E ISOtech'
    'int':      u'\u222B', # integral, U+222B ISOtech'
    'iota':     u'\u03B9', # greek small letter iota, U+03B9 ISOgrk3'
    'iquest':   u'\u00BF', # inverted question mark = turned question mark, U+00BF ISOnum'
    'isin':     u'\u2208', # element of, U+2208 ISOtech'
    'iuml':     u'\u00EF', # latin small letter i with diaeresis, U+00EF ISOlat1'
    'kappa':    u'\u03BA', # greek small letter kappa, U+03BA ISOgrk3'
    'lArr':     u'\u21D0', # leftwards double arrow, U+21D0 ISOtech'
    'lambda':   u'\u03BB', # greek small letter lambda, U+03BB ISOgrk3'
    'lang':     u'\u2329', # left-pointing angle bracket = bra, U+2329 ISOtech'
    'laquo':    u'\u00AB', # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum'
    'larr':     u'\u2190', # leftwards arrow, U+2190 ISOnum'
    'lceil':    u'\u2308', # left ceiling = apl upstile, U+2308 ISOamsc'
    'ldquo':    u'\u201C', # left double quotation mark, U+201C ISOnum'
    'le':       u'\u2264', # less-than or equal to, U+2264 ISOtech'
    'lfloor':   u'\u230A', # left floor = apl downstile, U+230A ISOamsc'
    'lowast':   u'\u2217', # asterisk operator, U+2217 ISOtech'
    'loz':      u'\u25CA', # lozenge, U+25CA ISOpub'
    'lrm':      u'\u200E', # left-to-right mark, U+200E NEW RFC 2070'
    'lsaquo':   u'\u2039', # single left-pointing angle quotation mark, U+2039 ISO proposed'
    'lsquo':    u'\u2018', # left single quotation mark, U+2018 ISOnum'
    'lt':       u'\u003C', # less-than sign, U+003C ISOnum'
    'macr':     u'\u00AF', # macron = spacing macron = overline = APL overbar, U+00AF ISOdia'
    'mdash':    u'\u2014', # em dash, U+2014 ISOpub'
    'micro':    u'\u00B5', # micro sign, U+00B5 ISOnum'
    'middot':   u'\u00B7', # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum'
    'minus':    u'\u2212', # minus sign, U+2212 ISOtech'
    'mu':       u'\u03BC', # greek small letter mu, U+03BC ISOgrk3'
    'nabla':    u'\u2207', # nabla = backward difference, U+2207 ISOtech'
    'nbsp':     u'\u00A0', # no-break space = non-breaking space, U+00A0 ISOnum'
    'ndash':    u'\u2013', # en dash, U+2013 ISOpub'
    'ne':       u'\u2260', # not equal to, U+2260 ISOtech'
    'ni':       u'\u220B', # contains as member, U+220B ISOtech'
    'not':      u'\u00AC', # not sign, U+00AC ISOnum'
    'notin':    u'\u2209', # not an element of, U+2209 ISOtech'
    'nsub':     u'\u2284', # not a subset of, U+2284 ISOamsn'
    'ntilde':   u'\u00F1', # latin small letter n with tilde, U+00F1 ISOlat1'
    'nu':       u'\u03BD', # greek small letter nu, U+03BD ISOgrk3'
    'oacute':   u'\u00F3', # latin small letter o with acute, U+00F3 ISOlat1'
    'ocirc':    u'\u00F4', # latin small letter o with circumflex, U+00F4 ISOlat1'
    'oelig':    u'\u0153', # latin small ligature oe, U+0153 ISOlat2'
    'ograve':   u'\u00F2', # latin small letter o with grave, U+00F2 ISOlat1'
    'oline':    u'\u203E', # overline = spacing overscore, U+203E NEW'
    'omega':    u'\u03C9', # greek small letter omega, U+03C9 ISOgrk3'
    'omicron':  u'\u03BF', # greek small letter omicron, U+03BF NEW'
    'oplus':    u'\u2295', # circled plus = direct sum, U+2295 ISOamsb'
    'or':       u'\u2228', # logical or = vee, U+2228 ISOtech'
    'ordf':     u'\u00AA', # feminine ordinal indicator, U+00AA ISOnum'
    'ordm':     u'\u00BA', # masculine ordinal indicator, U+00BA ISOnum'
    'oslash':   u'\u00F8', # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1'
    'otilde':   u'\u00F5', # latin small letter o with tilde, U+00F5 ISOlat1'
    'otimes':   u'\u2297', # circled times = vector product, U+2297 ISOamsb'
    'ouml':     u'\u00F6', # latin small letter o with diaeresis, U+00F6 ISOlat1'
    'para':     u'\u00B6', # pilcrow sign = paragraph sign, U+00B6 ISOnum'
    'part':     u'\u2202', # partial differential, U+2202 ISOtech'
    'permil':   u'\u2030', # per mille sign, U+2030 ISOtech'
    'perp':     u'\u22A5', # up tack = orthogonal to = perpendicular, U+22A5 ISOtech'
    'phi':      u'\u03C6', # greek small letter phi, U+03C6 ISOgrk3'
    'pi':       u'\u03C0', # greek small letter pi, U+03C0 ISOgrk3'
    'piv':      u'\u03D6', # greek pi symbol, U+03D6 ISOgrk3'
    'plusmn':   u'\u00B1', # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum'
    'pound':    u'\u00A3', # pound sign, U+00A3 ISOnum'
    'prime':    u'\u2032', # prime = minutes = feet, U+2032 ISOtech'
    'prod':     u'\u220F', # n-ary product = product sign, U+220F ISOamsb'
    'prop':     u'\u221D', # proportional to, U+221D ISOtech'
    'psi':      u'\u03C8', # greek small letter psi, U+03C8 ISOgrk3'
    'quot':     u'\u0022', # quotation mark = APL quote, U+0022 ISOnum'
    'rArr':     u'\u21D2', # rightwards double arrow, U+21D2 ISOtech'
    'radic':    u'\u221A', # square root = radical sign, U+221A ISOtech'
    'rang':     u'\u232A', # right-pointing angle bracket = ket, U+232A ISOtech'
    'raquo':    u'\u00BB', # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum'
    'rarr':     u'\u2192', # rightwards arrow, U+2192 ISOnum'
    'rceil':    u'\u2309', # right ceiling, U+2309 ISOamsc'
    'rdquo':    u'\u201D', # right double quotation mark, U+201D ISOnum'
    'real':     u'\u211C', # blackletter capital R = real part symbol, U+211C ISOamso'
    'reg':      u'\u00AE', # registered sign = registered trade mark sign, U+00AE ISOnum'
    'rfloor':   u'\u230B', # right floor, U+230B ISOamsc'
    'rho':      u'\u03C1', # greek small letter rho, U+03C1 ISOgrk3'
    'rlm':      u'\u200F', # right-to-left mark, U+200F NEW RFC 2070'
    'rsaquo':   u'\u203A', # single right-pointing angle quotation mark, U+203A ISO proposed'
    'rsquo':    u'\u2019', # right single quotation mark, U+2019 ISOnum'
    'sbquo':    u'\u201A', # single low-9 quotation mark, U+201A NEW'
    'scaron':   u'\u0161', # latin small letter s with caron, U+0161 ISOlat2'
    'sdot':     u'\u22C5', # dot operator, U+22C5 ISOamsb'
    'sect':     u'\u00A7', # section sign, U+00A7 ISOnum'
    'shy':      u'\u00AD', # soft hyphen = discretionary hyphen, U+00AD ISOnum'
    'sigma':    u'\u03C3', # greek small letter sigma, U+03C3 ISOgrk3'
    'sigmaf':   u'\u03C2', # greek small letter final sigma, U+03C2 ISOgrk3'
    'sim':      u'\u223C', # tilde operator = varies with = similar to, U+223C ISOtech'
    'spades':   u'\u2660', # black spade suit, U+2660 ISOpub'
    'sub':      u'\u2282', # subset of, U+2282 ISOtech'
    'sube':     u'\u2286', # subset of or equal to, U+2286 ISOtech'
    'sum':      u'\u2211', # n-ary sumation, U+2211 ISOamsb'
    'sup':      u'\u2283', # superset of, U+2283 ISOtech'
    'sup1':     u'\u00B9', # superscript one = superscript digit one, U+00B9 ISOnum'
    'sup2':     u'\u00B2', # superscript two = superscript digit two = squared, U+00B2 ISOnum'
    'sup3':     u'\u00B3', # superscript three = superscript digit three = cubed, U+00B3 ISOnum'
    'supe':     u'\u2287', # superset of or equal to, U+2287 ISOtech'
    'szlig':    u'\u00DF', # latin small letter sharp s = ess-zed, U+00DF ISOlat1'
    'tau':      u'\u03C4', # greek small letter tau, U+03C4 ISOgrk3'
    'there4':   u'\u2234', # therefore, U+2234 ISOtech'
    'theta':    u'\u03B8', # greek small letter theta, U+03B8 ISOgrk3'
    'thetasym': u'\u03D1', # greek small letter theta symbol, U+03D1 NEW'
    'thinsp':   u'\u2009', # thin space, U+2009 ISOpub'
    'thorn':    u'\u00FE', # latin small letter thorn with, U+00FE ISOlat1'
    'tilde':    u'\u02DC', # small tilde, U+02DC ISOdia'
    'times':    u'\u00D7', # multiplication sign, U+00D7 ISOnum'
    'trade':    u'\u2122', # trade mark sign, U+2122 ISOnum'
    'uArr':     u'\u21D1', # upwards double arrow, U+21D1 ISOamsa'
    'uacute':   u'\u00FA', # latin small letter u with acute, U+00FA ISOlat1'
    'uarr':     u'\u2191', # upwards arrow, U+2191 ISOnum'
    'ucirc':    u'\u00FB', # latin small letter u with circumflex, U+00FB ISOlat1'
    'ugrave':   u'\u00F9', # latin small letter u with grave, U+00F9 ISOlat1'
    'uml':      u'\u00A8', # diaeresis = spacing diaeresis, U+00A8 ISOdia'
    'upsih':    u'\u03D2', # greek upsilon with hook symbol, U+03D2 NEW'
    'upsilon':  u'\u03C5', # greek small letter upsilon, U+03C5 ISOgrk3'
    'uuml':     u'\u00FC', # latin small letter u with diaeresis, U+00FC ISOlat1'
    'weierp':   u'\u2118', # script capital P = power set = Weierstrass p, U+2118 ISOamso'
    'xi':       u'\u03BE', # greek small letter xi, U+03BE ISOgrk3'
    'yacute':   u'\u00FD', # latin small letter y with acute, U+00FD ISOlat1'
    'yen':      u'\u00A5', # yen sign = yuan sign, U+00A5 ISOnum'
    'yuml':     u'\u00FF', # latin small letter y with diaeresis, U+00FF ISOlat1'
    'zeta':     u'\u03B6', # greek small letter zeta, U+03B6 ISOgrk3'
    'zwj':      u'\u200D', # zero width joiner, U+200D NEW RFC 2070'
    'zwnj':     u'\u200C'  # zero width non-joiner, U+200C NEW RFC 2070'
}

entitydefs2 = {
    '$':    '%24',
    '&':    '%26',
    '+':    '%2B',
    ',':    '%2C',
    '/':    '%2F',
    ':':    '%3A',
    ';':    '%3B',
    '=':    '%3D',
    '?':    '%3F',
    '@':    '%40',
    ' ':    '%20',
    '"':    '%22',
    '<':    '%3C',
    '>':    '%3E',
    '#':    '%23',
    '%':    '%25',
    '{':    '%7B',
    '}':    '%7D',
    '|':    '%7C',
    '\\':   '%5C',
    '^':    '%5E',
    '~':    '%7E',
    '[':    '%5B',
    ']':    '%5D',
    '`':    '%60'
}

entitydefs3 = {
    u'ÂÁÀÄÃÅ':  u'A',
    u'âáàäãå':  u'a',
    u'ÔÓÒÖÕ':   u'O',
    u'ôóòöõðø': u'o',
    u'ÛÚÙÜ':    u'U',
    u'ûúùüµ':   u'u',
    u'ÊÉÈË':    u'E',
    u'êéèë':    u'e',
    u'ÎÍÌÏ':    u'I',
    u'îìíï':    u'i',
    u'ñ':       u'n',
    u'ß':       u'B',
    u'÷':       u'%',
    u'ç':       u'c',
    u'æ':       u'ae'
}

def clean1(s): # remove &XXX;
    if not s:
        return ''
    for name, value in entitydefs.iteritems():
        if u'&' in s:
            s = s.replace(u'&' + name + u';', value)
    return s;

def clean2(s): # remove \\uXXX
    pat = re.compile(r'\\u(....)')
    def sub(mo):
        return unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))

def clean3(s): # remove &#XXX;
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return decode(pat.sub(sub, smart_unicode(s)))

def decode(s):
    if not s:
        return ''
    try:
        dic=htmlentitydefs.name2codepoint
        for key in dic.keys():
            entity = '&' + key + ';'
            s = s.replace(entity, unichr(dic[key]))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def unquote_safe(s): # unquote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s;

def quote_safe(s): # quote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s;


def clean_safe(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s))))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def first_clean_filename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '')
    return s;

def second_clean_filename(s):
    if not s:
        return ''
    for key, value in entitydefs3.iteritems():
        for c in key:
            s = s.replace(c, value)
    return s;

def third_clean_filename(s):
    if not s:
        return ''
    validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
    stripped = ''.join(c for c in s if c in validchars)
    return stripped;

def randomFilename(dir = cacheDir, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 10000):
    for attempt in range(attempts):
        filename = ''.join([random.choice(chars) for i in range(length)])
        filename = prefix + filename + suffix
        if not os.path.exists(os.path.join(dir, filename)):
            return filename


def getKeyboard(default = '', heading = '', hidden = False):
    kboard = xbmc.Keyboard(default, heading, hidden)
    kboard.doModal()
    if kboard.isConfirmed():
        return urllib.quote_plus(kboard.getText())
    return ''

def showMessage(msg):
    xbmc.executebuiltin('Notification(SportsDevil,' + str(msg) + ')')

def showDialog(msg, timeout=0):
    dialog = xbmcgui.Dialog()
    dialog.ok('SportsDevil Info', msg)
    if timeout > 0:
        xbmc.sleep(timeout * 1000)
        dialog.close()


def firstNonEmpty(tmp, vars):
    for v in vars:
        vClean = v.strip()
        if vClean.find("'") != -1:
            vClean = vClean.strip("'")
        else:
            vClean = tmp.getInfo(vClean)

        if vClean != '':
            return vClean

    return ''


def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def safeRegexEncoding(regex):
    tmp = ''
    for i in range(0,len(regex),1):
        if regex[i] in ('(', ')', '?'):
            tmp += '.'
        else:
            try:
                regex[i].encode('ascii')
                tmp += regex[i]
            except:
                tmp += '.{1,2}'
                continue
    return tmp

def safeGerman(src):
    try:
        src = src.encode('latin-1')
    except:
        log('Unicode Error')

    tmp = '[^<]*'

    try:
        src = src.replace('ä',tmp)
    except:
        try:
            src = src.replace(u'ä',tmp)
        except:
            if enable_debug:
                log('Unicode Error')

    try:
        src = src.replace('&#223;',tmp)
    except:
        try:
            src = src.replace(u'&#223;',tmp)
        except:
            if enable_debug:
                xbmc.output('Unicode Error')

    return src


def timediff(mytime, unit='seconds'):
    dtNow = datetime.datetime.utcnow()
    datePart = mytime.split(' ')[0]
    dpArr = datePart.split('/')
    timePart = mytime.split(' ')[1]
    tpArr = timePart.split(':')
    d = datetime.date(int(dpArr[0]), int(dpArr[1]), int(dpArr[2]))
    t = datetime.time(int(tpArr[0]), int(tpArr[1]))
    dt = datetime.datetime.combine(d,t)

    diff = dtNow - dt

    if unit == 'seconds':
        return str(diff.seconds)
    elif unit == 'minutes':
        return str(diff.seconds/60)
    elif unit == 'sapo':
        #Math.floor(new Date().getTime()/1000)-Math.floor(new Date().getTime()/1000)-time
        #return str(1304805500 + diff.seconds*75)
        return time.time()
    else:
        return '0'

def getFileContent(filename):
    try:
        f = open(filename,'r')
        txt = f.read()
        f.close()
        return txt
    except:
        return ''

def setFileContent(filename, txt):
    try:
        f = open(filename, 'w')
        f.write(smart_unicode(txt).encode('utf-8'))
        f.close()
        return True
    except:
        return False

def appendFileContent(filename, txt):
    try:
        f = open(filename, 'a')
        f.write(smart_unicode(txt).encode('utf-8'))
        f.close()
        return True
    except:
        return False


def convDate(datestr, frmt, newfrmt = ''):
    ''''
    locale.setlocale(locale.LC_ALL, '')
    try:
        c = time.strptime(str(datestr).rstrip(),str(smart_unicode(frmt)).rstrip())
    except:
        xbmc.output('conversion failed')
        return datestr

    if c.tm_year != 1900:
        return time.strftime("%y/%m/%d",c)
    else:
        return time.strftime("%m/%d",c)
    '''

    try:
        datestr = datestr.encode('utf-8')
    except:
        datestr = datestr

    monthsEN = {
        'January':  1,
        'February': 2,
        'March':    3,
        'April':    4,
        'May':      5,
        'June':     6,
        'July':     7,
        'August':   8,
        'September':9,
        'October':  10,
        'November': 11,
        'December': 12
    }

    monthsDE = {
        'Januar':   1,
        'Februar':  2,
        u'März':    3,
        'Maerz':    3,
        'April':    4,
        'Mai':      5,
        'Juni':     6,
        'Juli':     7,
        'August':   8,
        'September':9,
        'Oktober':  10,
        'November': 11,
        'Dezember': 12
    }

    datesyms = {
        #DAY
        '%d':'\d{1,2}',
        '%a':'\w{3}',
        '%A':'[A-Za-z]{3}',

        #MONTH
        '%m':'\d{2}',
        '%b':'\w{3}',
        '%B':'\w{3,}',

        #YEAR
        '%y':'\d{2}',
        '%Y':'\d{4}',

        #HOUR
        '%H':'\d{2}',
        '%I':'\d{1,2}',

        #AM/PM
        '%p':'\w{2}',
        '%P':'\w{2}',

        #MINUTE/SECOND
        '%M':'\d{2}',
        '%S':'\d{2}'
    }

    language = xbmc.getLanguage()
    if lower(language).startswith('german'):
        months = monthsDE
    else:
        months = monthsEN

    patFrmt = '(%\w)'
    idxFrmt = re.findall(patFrmt,frmt, re.DOTALL + re.IGNORECASE)

    try:
        for item in idxFrmt:
            if datesyms.has_key(item):
                frmt = frmt.replace(item,'(' + datesyms[item] + ')')
            else:
                log('missing: ' + item)

        p = re.compile(frmt, re.DOTALL + re.IGNORECASE)
        try:
            datestr = datestr.replace('ä','ae')  # ä
        except:
            datestr = datestr.replace(u'ä','ae')   # ä

        try:
            datestr = datestr.replace('\xe4','ae')
        except:
            pass

        m = p.match(datestr)
        if not m:
            return datestr

        second = 1
        minute = 1
        hour = 1
        day = 1
        month = 1
        year = 1900

        for item in m.groups(0):
            if not (idxFrmt[list(m.groups(0)).index(item)] is None):
                sym = idxFrmt[list(m.groups(0)).index(item)]
                if sym == '%B':
                    if monthsDE.has_key(item.capitalize()):
                        month = monthsDE[item.capitalize()]
                        continue
                    if monthsEN.has_key(item.capitalize()):
                        month = monthsEN[item.capitalize()]
                        continue
                elif sym == '%m':
                    month = int(item)
                elif sym == '%d':
                    day = int(item)
                elif sym == '%y' or sym == '%Y':
                    year = int(item)
                elif sym == '%H':
                    hour = int(item)
                elif sym == '%M':
                    minute = int(item)
                elif sym == '%S':
                    second = int(item)

        date = datetime.date(year,month,day)

        if newfrmt == '':
            if date.year != 1900:
                newfrmt = "%y/%m/%d"
            else:
                newfrmt = "%m/%d"

        return date.strftime(newfrmt)
    except:
      log('Conversion failed')
      traceback.print_exc(file = sys.stdout)
      return datestr

def encryptDES_ECB(data, key):
    data = data.encode()
    k = pyDes.des(key, pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    assert k.decrypt(d, padmode=pyDes.PAD_PKCS5) == data
    return d

def encryptJimey(data):
    result = encryptDES_ECB(data,"PASSWORD").encode('base64').replace('/','').strip()
    return result

def hp_d01(s):
    o=""
    ar=[]
    os=""
    for i in range(0,len(s)-1):
        c = ord(s[i])
        if c < 128:
            c = c^2
        os += chr(c)
        if len(os) > 80:
            ar.append(os)
            os = ""
    o = join(ar,'') + os
    return o

def o61a2a8f(s):
    r = "";
    tmp = s.split("18267506");
    s = urllib.unquote(tmp[0]);
    k = urllib.unquote(tmp[1] + "511382");
    for i in range(0,len(s)-1):
        r += chr((int(k[i%len(k)])^ord(s[i]))+1);
    return r;

def n98c4d2c(s):
    txtArr = s.split('18234663')
    s = urllib.unquote(txtArr[0])
    t = urllib.unquote(txtArr[1] + '549351')
    tmp=''
    for i in range(0,len(s)-1):
        tmp += chr((int(t[i%len(t)])^ord(s[i]))+-6)
    return urllib.unquote(tmp)

def RrRrRrRr(teaabb):
    tttmmm=""
    l=len(teaabb)
    www = hhhhffff = int(round(l/2))
    if l<2*www:
        hhhhffff -= 1
    for i in range(0,hhhhffff-1):
        tttmmm = tttmmm + teaabb[i] + teaabb[i+hhhhffff]
    if l<2*www :
        tttmmm = tttmmm + teaabb[l-1]
    return tttmmm

def ew_dc(s):
    d=''
    a=[]
    for i in range(0, len(s)-1):
        c = ord(s[i])
        if (c<128):
            c = c^5
        d += chr(c)
        if (i+1) % 99 == 0:
            a.append(d)
            d=''
    r = join(a,'') + d
    return r

def pbbfa0(s):
    r = ""
    tmp = s.split("17753326")
    s = urllib.unquote(tmp[0])
    k = urllib.unquote(tmp[1] + "527117")
    for i in range(0,len(s)):
    	r += chr((int(k[i%len(k)])^ord(s[i]))+7)
    return r

# used by 24cast
def destreamer(s):
    #remove all but[0-9A-Z]
    str = re.sub("[^0-9A-Z]", "", s.upper())
    result = ""
    nextchar = ""
    for i in range(0,len(str)-1):
        nextchar += str[i]
        if len(nextchar) == 2:
            result += ntos(int(nextchar,16))
            nextchar = ""
    return result

def ntos(n):
    n = hex(n)[2:]
    if len(n) == 1:
        n = "0" + n
    n = "%" + n
    return urllib.unquote(n)

def getUnixTimestamp():
    return int(time.time())

def getSource(page, referer='', demystify=False):

    url = urllib.unquote_plus(page)
    if referer == '':
        referer = url

    txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
    req = Request(url, None, txheaders)
    req.add_header('Referer', referer)

    try:
        handle = urlopen(req)
    except:
        log('Page: \'' + url + '\' could not be opened' )
        info = sys.exc_info()
        showMessage(str(info[1]))
        traceback.print_exc(file = sys.stdout)
        return ''

    data = handle.read()
    handle.close()

    if not demystify:
        # remove comments
        r = re.compile('<!--.*?(?!//)-->', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        m = r.findall(data)
        if m:
            for comment in m:
                data = data.replace(comment,'')
    else:
        data = doDemystify(data)

    #cj.save(os.path.join(cacheDir, 'cookies.lwp'), ignore_discard=True)
    cj.save(os.path.join(cacheDir, 'cookies.lwp'))

    return data


def doDemystify(data):

    # unescape
    r = re.compile('unescape\(\s*["\']([^\'"]+)["\']')
    gs = r.findall(data)
    if gs:
        for g in gs:
            quoted=g
            data = data.replace(quoted, urllib.unquote_plus(quoted))

    # n98c4d2c
    if data.find('function n98c4d2c(') > -1:
        gs = parseTextToGroups(data, ".*n98c4d2c\(''\).*?'(%[^']+)'.*")
        if gs != None and gs != []:
            data = data.replace(gs[0],n98c4d2c(gs[0]))

    # o61a2a8f
    if data.find('function o61a2a8f(') > -1:
        gs = parseTextToGroups(data, ".*o61a2a8f\(''\).*?'(%[^']+)'.*")
        if gs != None and gs != []:
            data = data.replace(gs[0],o61a2a8f(gs[0]))

    # RrRrRrRr
    if data.find('function RrRrRrRr(') > -1:
        r = re.compile("(RrRrRrRr\(\"(.*?)\"\);)</SCRIPT>", re.IGNORECASE + re.DOTALL)
        gs = r.findall(data)
        if gs != None and gs != []:
            for g in gs:
                data = data.replace(g[0],RrRrRrRr(g[1].replace('\\','')))

    # hp_d01
    if data.find('function hp_d01(') > -1:
        r = re.compile("hp_d01\(unescape\(\"(.+?)\"\)\);//-->")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,hp_d01(g))

    # ew_dc
    if data.find('function ew_dc(') > -1:
        r = re.compile("ew_dc\(unescape\(\"(.+?)\"\)\);</SCRIPT>")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,ew_dc(g))

    # pbbfa0
    if data.find('function pbbfa0(') > -1:
        r = re.compile("pbbfa0\(''\).*?'(.+?)'.\+.unescape")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,pbbfa0(g))


    # util.de
    if data.find('Util.de') > -1:
        r = re.compile("Util.de\(unescape\(['\"](.+?)['\"]\)\)")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,g.decode('base64'))

    # 24cast
    if data.find('destreamer(') > -1:
        r = re.compile("destreamer\(\"(.+?)\"\)")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,destreamer(g))


    # Tiny url
    r = re.compile('[\'"](http://(?:www.)?tinyurl.com/[^\'"]+)[\'"]',re.IGNORECASE + re.DOTALL)
    m = r.findall(data)
    if m:
        for tiny in m:
            data = data.replace(tiny,get_redirected_url(tiny))

    return data


def get_redirected_url(url):
    import urllib2
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

def findRedirect(page, demystify=False):
    data = getSource(page, '', demystify)
    if data.find('frame') > -1 or data.find('FRAME') > -1:
        r = re.compile("(frame[^>]* height=[\"']*(\d+)[\"']*[^>]*>)", re.IGNORECASE + re.DOTALL)
        iframes = r.findall(data)

        if iframes:
            for iframe in iframes:

                height = int(iframe[1])
                if height > 300:
                    r = re.compile("[ ]width=[\"']*(\d+[%]*)[\"']*", re.IGNORECASE  + re.DOTALL)
                    m = r.findall(iframe[0])
                    if m:
                        if m[0] == '100%':
                            width = 301
                        else:
                            width = int(m[0])
                        if width > 300:
                            r = re.compile('[\'"\s]src=["\']*\s*([^"\' ]+)\s*["\']*', re.IGNORECASE + re.DOTALL)
                            m = r.findall(iframe[0])
                            if m:
                                link = m[0]
                                if not link.startswith('http://'):
                                    from urlparse import urlparse
                                    up = urlparse(urllib.unquote(page))
                                    if link.startswith('/'):
                                        link = urllib.basejoin(up[0] + '://' + up[1],link)
                                    else:
                                        link = urllib.basejoin(up[0] + '://' + up[1] + '/' + up[2],link)
                                return link.strip()

        # Alternative 1
        r = re.compile("(frame[^>]*[\"; ]height:\s*(\d+)[^>]*>)", re.IGNORECASE + re.DOTALL)
        iframes = r.findall(data)
        if iframes:
            for iframe in iframes:
                height = int(iframe[1])
                if height > 300:
                    r = re.compile("[\"; ]width:\s*(\d+)", re.IGNORECASE  + re.DOTALL)
                    m = r.findall(iframe[0])
                    if m:
                        width = int(m[0])
                        if width > 300:
                            r = re.compile('[ ]src=["\']*\s*([^"\' ]+)\s*["\']*', re.IGNORECASE + re.DOTALL)
                            m = r.findall(iframe[0])
                            if m:
                                link = m[0]
                                if not link.startswith('http://'):
                                    link = urllib.basejoin(page,link)
                                return link.strip()

        # Alternative 2 (Frameset)
        r = re.compile('<FRAMESET[^>]+100%[^>]+>\s*<FRAME[^>]+src="([^"]+)"', re.IGNORECASE + re.DOTALL)
        iframes = r.findall(data)
        if iframes:
            link = iframes[0]
            if not link.startswith('http://'):
                link = urllib.basejoin(page,link)
            return link.strip()

    if not demystify:
        return findRedirect(page, True)

    return page

def parseTextToGroups(txt, regex):
    p = re.compile(regex, re.IGNORECASE + re.DOTALL + re.MULTILINE)
    m = p.match(smart_unicode(txt))
    if m:
        return m.groups()
    else:
        return None


def parseWebsiteToGroups(url, regex, referer=''):
    data = getSource(url,referer)
    return parseTextToGroups(data, regex)


def parseText(txt, regex, vars=[]):
    groups = parseTextToGroups(txt, regex)
    if vars == []:
        if groups:
            return groups[0]
        else:
            return ''
    else:
        resultArr = {}
        i = 0
        for v in vars:
            if groups:
                resultArr[v] = groups[i]
            else:
                resultArr[v] = ''
            i += 1
        return resultArr


def parseWebsite(source, regex, referer='', vars=[]):
    groups = parseWebsiteToGroups(source, regex, referer)

    if vars == []:
        if groups:
            return groups[0]
        else:
            return ''
    else:
        resultArr = {}
        i = 0
        for v in vars:
            if groups:
                resultArr[v] = groups[i]
            else:
                resultArr[v] = ''
            i += 1
        return resultArr

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def findall(data,regex):
    p_reg = re.compile(regex, re.IGNORECASE + re.DOTALL + re.MULTILINE)
    result = p_reg.findall(data)
    return result

def log(msg):
    if enable_debug:
        xbmc.log(msg)
        #xbmc.output(msg)

def ifStringEmpty(str, trueStr, falseStr):
    if str == '':
        return trueStr
    else:
        return falseStr

def isOnline(url):
    txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
    req = Request(url, None, txheaders)
    try:
        handle = urlopen(req)
        return True
    except:
        return False

def ifExists(url, trueStr, falseStr):
    if isOnline(url):
        return trueStr
    else:
        return falseStr

def findInSubdirectory(filename, subdirectory=''):
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, dirs, names in os.walk(path):
        if filename in names:
            return os.path.join(root, filename)
    raise 'File not found'
