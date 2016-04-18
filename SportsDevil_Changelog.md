# Changelog #

V1.8.5.5:
  * modules:
    * FIX: livetv.ru
    * MERGE: modules repo

  * catchers:
    * ADD: HTTP: files
    * MERGE: catchers repo
  * addon:
    * CHG: added JavaScript (p,a,c,k,e,d) unpacking to demystification
    * ADD: conversion function convTimestamp(newformat, offsetString='')
    * FIX: removal of favourites with unicode titles
    * FIX: empty favourite folders are shown instead of 'No stream available'
    * FIX: renaming virtual folders will update the header too
    * CHG: virtual folders are not limited to one level any more
    * CHG: renamed settings category "Actions" to "Updates" and moved auto-update setting there
    * FIX: autoupdate when addon is started from favourite/custom mainmenu entry
    * ADD: install external addons JustinTV, YouTube and Veetle via settings

<br>

V1.8.2:<br>
<ul><li>FIX: import python module from parent folder<br>
</li><li>FIX: coolsportz.de.cfg, set referer<br>
</li><li>ADD: catcher vipi</li></ul>

<br>

V1.8.1.1:<br>
<ul><li>fix: streamer viovu: use referer (@REFERER@) => snsports working now<br>
</li><li>change: change referer in case of redirect<br>
</li></ul><blockquote>You need the current version of librtmp. See <a href='http://wiki.xbmc.org/index.php?title=librtmp'>http://wiki.xbmc.org/index.php?title=librtmp</a></blockquote>

<br>
V1.8.1:<br>
<ul><li>further refactoring<br>
</li><li>more precise parsing error messages<br>
</li><li>fixed favourites<br>
</li><li>begin of syntax refactoring: new list skills: referer (sets item url as referer for further links/streamers), videoTitle (sets item title as video title)<br>
</li><li>fixed cookiehandling<br>
</li><li>some new icons, some icons sorted out<br>
</li><li>sports icons moved to subfolder</li></ul>

<br>
V1.8:<br>
<br>
<ul><li>almost completely refactored / restructured / reorganized<br>
</li><li>fixed favourites management<br>
</li><li>merged fixed/new streamers by al101:<br>
</li><li>fixed: aliez, castalba, castto, tvope<br>
</li><li>new: fcast, vivocast, yourlivetv<br>
</li><li>fixed some bugs and sites (lshunter still not working)</li></ul>

<br>
V1.7.6:<br>
<ul><li>merged fixed / new streamers of al101 (thanks again Smile):<br>
</li><li>New: BLive, Casti, FlashWiz, LiveAll, Sike, Stream4u, StreamAll, StreamGenie and Vcaster.<br>
</li><li>Fixed: Zcast, ReyHD, Cast3d and Tutele.<br>
</li><li>fixed streamer 04stream (responsible for "Unkown URL Type: <a href='http://www.TheFirstRow.EU'>http://www.TheFirstRow.EU</a>.")<br>
</li><li>added site snsports.tv in tv section (thanks to k1m0s)</li></ul>

<br>
V1.7.5:<br>
<blockquote>Thanks to al101<br>
Merged his works.</blockquote>

<ul><li>new sites: cricfree, hdfooty<br>
</li><li>new streamers:<br>
<ul><li>launchlive<br>
</li><li>flashi<br>
</li><li>yocast<br>
</li><li>tvbay<br>
</li></ul></li><li>fixed streamers:<br>
<ul><li>yycast<br>
</li><li>veemi<br>
</li><li>mips<br>
</li><li>liveflash<br>
</li><li>hqcast<br>
</li><li>ucaster<br>
</li><li>streamhq<br>
</li><li>limev<br>
</li><li>ilive</li></ul></li></ul>

<br>
V1.7.4.4<br>
<ul><li>FIX: firstrowsports.eu (new url) THX to jakeculpin<br>
</li><li>FIX: 04stream: new url of firstrowsports as referrer<br>
</li><li>CHG: xsopcast will be used automatically on linux (xsopcast must be installed) THX to ecinema</li></ul>

<br>
V1.7.4.3.1:<br>
<ul><li>quick fix for streamer buzzin (thanks to k1m0s for his PM)</li></ul>

<br>
V1.7.4.3:<br>
<ul><li>fixed coolsportz.de aka coolsport.tv<br>
</li><li>some schedule entries are not shown, but I can't find the mistake in my regular expression. maybe someone else does...</li></ul>

<br>
V1.7.4.2:<br>
<ul><li>fixed rojadirecta.me:<br>
<ul><li>recognition of p2p streams<br>
</li><li>regular expression: now all links should be found, all bet streams filtered out.<br>
</li></ul></li><li>fixed the "can't find favourites folder" bug</li></ul>

<br>
V1.7.4.1:<br>
<ul><li>fixed a small bug in favouritesManager (variable not initialized under certain circumstances)</li></ul>

<br>
V1.7.4:<br>
<ul><li>fixed sites: goalsarena.org, chanfeed.com<br>
</li><li>fixed streamers: castalba, castamp, mips, sawlive, surktv<br>
</li><li>added streamer: eplayer<br>
</li><li>some small fixes and improvements</li></ul>

<br>
V1.7.3.1:<br>
<ul><li>fixed site coolsportz.de (small unicode error)</li></ul>

<br>
V1.7.3:<br>
<ul><li>fixed site lshunter.tv<br>
</li><li>added site coolsportz.de</li></ul>

<br>
V1.7.2:<br>
<ul><li>changed: quality of sport1.de videos set to medium<br>
</li><li>fixed search in section lshunter.tv<br>
</li><li>fixed streamer dailymotion<br>
</li><li>a lot of refactoring and speedup</li></ul>

<br>
V1.7.1:<br>
<ul><li>added streamer buzzin<br>
</li><li>fixed site livetv.ru (live sports)</li></ul>

<br>
V1.7.0.1:<br>
<ul><li>fix: create SportsDevil addon_data folder if it doesn't exist</li></ul>

<br>
V1.7:<br>
<ul><li>fixed streamer megom<br>
</li><li>added favourites management for both SportsDevil and xbmc favourites; favourites can be organized in folders (only one level)<br>
</li><li>some refactoring</li></ul>

<br>
V1.6.5.5:<br>
<ul><li>added site: vipbox.tv (thanks to Gainesway1 for the icon)<br>
</li><li>some small fixes and improvements</li></ul>

<br>
V1.6.5.4:<br>
<ul><li>fixed streamers: justintv (fallback flashplayer), livebox, livevdo, vshare<br>
</li><li>new streamers: castup, hqcast, megom, redcast, sawlive, surktv<br>
</li><li>fixed site rojadirecta.me (some links were not scraped)<br>
</li><li>changed site livetv.ru so new streamers are recognized</li></ul>

<br>
V1.6.5.3:<br>
<ul><li>fixed streamers: veemi, yycast, streamhq, xuuby, zonein, limev, justintv, aliez, castamp<br>
</li><li>new streamers: ilive, castalba, 24cast, 04stream, tvcaston, liveflash, scity, ucaster (no working stream found so far), mybcast, xstit, yourlivetv, letontv, cast3d, zcast<br>
</li><li>fixed sites: chanfeed.com, firstrowsports.eu<br>
</li><li>changed site livetv.ru so new streamers are recognized<br>
</li><li>removed site soccerhd.info (site doesn't provide streams anymore)</li></ul>

<br>
V1.6.5:<br>
<ul><li>much of the code rewritten and cleaned<br>
</li><li>added streamers: JustinTV<br>
</li><li>fixed some streamers: CastAmp, SeeOn, ...<br>
</li><li>improved detection of redirects<br>
</li><li>improved de-mystification of html source code<br>
</li><li>new context menu item 'Queue': adds both folders and videos to the current video playlist (folders are scanned for videos first). Please don't use the queue key on your remote (if configured) or 'q', if 'autoplay' is enabled. You can always use the context menu item.</li></ul>

<blockquote>This new option allows you to:<br>
<ul><li>make a simulcast of several matches<br>
</li><li>easily change to another stream if the current one is overloaded<br>
</li><li>create a playlist of tv channels and save it for later usage</li></ul></blockquote>

<blockquote>A known bug of this new feature is, that the current playlist is cleared by xbmc whenever an error occurs while trying to play a certain stream. I don't know why it doesn't just skip this item like it does with offline streams.<br>
</blockquote><ul><li>new context menu option 'Download'<br>
</li><li>new sites:<br>
<ul><li>TV<br>
<ul><li>LiveSportsOnWeb<br>
</li><li>Twww.TV<br>
</li><li>PutPat.tv<br>
</li><li>ShadowNet.ro<br>
</li><li>MyPremium.tv</li></ul></li></ul></li></ul>

<ul><li>Live Sports<br>
<ul><li>SoccerHD.info<br>
</li><li>RojaDirecta.me</li></ul></li></ul>

<ul><li>language is now detected automatically<br>
</li><li>player is set to auto by default<br></li></ul>

<br>
V1.6.4:<br>
<ul><li>added streamers: Rey, 24in, Hogy, Laola1 (livestreams), LiveBox, MegaLive, Streami, TuTele, VipLive, Rede.tv, Myp2p.in, ASF, M3U8, ProTV, Nacevi, Guarapa, Globo + several direct RTMPs<br>
</li><li>fixed streamers here and there<br>
</li><li>added many hardcoded redirects + some intelligence to detect redirects automatically (working pretty good)<br>
</li><li>single folders are selected automatically on certain pages<br>
</li><li>added setting: autoplay (play single video in a list automatically)<br>
</li><li>added setting: timeoffset (auto correct times, experimental)<br>
</li><li>autoselection and autoplay should bring you straight to the embedded video and play it<br>
</li><li>added site: lshunter.tv (thanks to GeorgeStroke for the nice logo)<br>
</li><li>fixed site: chanfeed.com<br>
</li><li>new section 'TV'<br>
</li><li>the addon now caches the current html source code =&gt; faster navigation, less traffic<br>
</li><li>a lot of refactoring (hope it wasn't too much)<br>
</li><li>many fixes</li></ul>

<br>
V1.6.3:<br>
<ul><li>fixed: chanfeed.com<br>
</li><li>added streamers: StreamHQ (stops after a few seconds), HDCaster, VShare, iCastOn, BoxLive, 786cast, OwnCast, VStream, Xuuby, JimeyTV, NCAA streams for chanfeed, Livefootballstreams.net for firstrowsports.eu<br>
</li><li>fixed streamer: ustream (should get every stream now), wii-cast (using token now)<br>
</li><li>prepared streamer: JustinTV (still have to find out how to pass the jtv token with whitespaces and quotation marks)<br>
</li><li>added many redirects, tinyurl decoding and html unquoting for firstrowsports.eu<br>
</li><li>many small fixes I can't remember in detail</li></ul>

<br>
V1.6.2:<br>
<ul><li>added site: chanfeed.com<br>
</li><li>added streamer: general rtmp (for livetv.ru), ustream, zecast<br>
</li><li>fixed streamer: rayson<br>
</li><li>addon fanart</li></ul>

<br>
V1.6.1:<br>
<ul><li>removed: myp2p (site is offline)<br>
</li><li>added streamer: liveVDO<br>
</li><li>fixed: zonein streams with old mechanism</li></ul>

<br>
V1.6.0:<br>
<ul><li>fixed: zonein, limev, seeon<br>
</li><li>added: streambig, mips, liveview365, svtplay, strmr<br>
</li><li>sport1.de: fixed regular expressions (site changed)<br>
</li><li>goalsarena.org: fixed links in categories<br>
</li><li>autoplay disabled for 2 reasons:<br>
<ol><li>sometimes, if another plugin is called, I get an error "called from invalid handle"<br>
</li><li>you can see which streamer is used and can therefore give better feedback about working status<br>
</li></ol></li><li>some other fixes and improvements</li></ul>

<br>
V1.5.0:<br>
<ul><li>fix for pre-eden builds<br>
</li><li>fix for xbox platform<br>
</li><li>sport1.de: the rss feed I took the links from went offline, so I did the parsing myself<br>
</li><li>autoplay for highlight streams<br>
</li><li>some other fixes and improvements</li></ul>

<br>
V1.4.0:<br>
<ul><li>livetv.ru - highlights: fixed links<br>
</li><li>far less clicks needed to resolve the stream url<br>
</li><li>myp2p.eu: categories now dynamically created<br>
</li><li>lots of changes to physical folder and file structure<br>
</li><li>Added: Yandex<br>
</li><li>Sports Icons (thanx to Hudson_Hawk04)<br>
</li><li>...<br>
</li><li>Syntax:<br>
<ul><li>new: 'section' (only parse a part of the page)<br>
</li><li>new methods for 'item_info_convert':<br>
</li></ul><blockquote>replaceFromDict(dictfile), getInfo(page,regex)<br>
</blockquote><ul><li>new: call cfg with more than one parameter<br>
</li><li>new: @CATCH(zonein,channel)@ defines a catcher per stream<br>
</li><li>...</li></ul></li></ul>

<br>
V1.3.0:<br>
<ul><li>livetv.ru - live: categories now dynamically created<br>
</li><li>livetv.ru - highlights: new folder structure<br>
</li><li>livetv.ru - highlights: browse competitions<br>
</li><li>some small fixes for youtube and yatv.ru<br>
</li><li>Added: VKontakte, Sapo<br>
</li><li>Syntax:<br>
<ul><li>new: 'section' (only parse a part of the page)<br>
</li><li>new: 'item_info_convert', methods: convDate(oldFormat,newFormat), timediff(dateStr)<br>
</li><li>new: call cfg with parameter (cfg=file.cfg@Hello) =&gt; (@PARAM1@ is replaced by 'Hello' in file.cfg)</li></ul></li></ul>

<br>
V1.2.0:<br>
<ul><li>xbox fix<br>
</li><li>livetv.ru regex fix<br>
</li><li>Added: Freedcocast, WebCastOn, YYCast</li></ul>

<br>
V1.1.0:<br>
<ul><li>fixed encoding bug<br>
</li><li>fixed os.getcwd() deprecation bug<br>
</li><li>LiveTV.ru: better sorting (04/26 instead of 26 April)</li></ul>

<br>
V1.0.1:<br>
<ul><li>fixed FirstRowSports.eu categories<br>
</li><li>improved FirstRowSports folder structure</li></ul>

<br>
V1.0:<br>
<ul><li>initial release</li></ul>

<br>
TODO (help needed):<br>

<ul><li>Streams:<br>
<ul><li>Livestream.com</li></ul></li></ul>

<ul><li>Features:<br>
<ul><li>Prefer some streams via settings<br>
</li><li>Support for favourite teams<br>
</li><li>Cooperation with the VideoFalcon project</li></ul></li></ul>

