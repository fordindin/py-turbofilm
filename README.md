What is this?
=============

py-turbofilm is very simple standalone python client for (not-so)popular
TV-series watching resource turbofilm. For now it turbik.tv

Turbofilm is not completely public resource, you should get invite somewhere to
use it.

Turbofilm is not free - there is small monthly fee (around 3$ per month).

Personaly I LOVE mplayer, (http://www.mplayerhq.hu/), and I hate Adobe Flash player (it 
uses to much power on my laptops and insanely unstable). So I wrote simple python client
to watch my favorite series in my favorite player.

I am deeply UNIX guy, so I only tested this on FreeBSD and MacOS X.

So, if you get to this point I will tell you how it works.

First of all you should somehow install mplayer (http://www.mplayerhq.hu/), py-turbofilm
uses it as a player. (On MacOS use brew, fink or MacPorts)

Next, you should specify your login in config.cf.

My favorite options are:

To show new and unseen episodes of your favorite series

dindin@laptop% turbofilm unseen

== 1    Glee
== 1    OnceUponATime
== 1    TheBigBangTheory
== 1    WhiteCollar
== 1    SouthPark
== 1    AngerManagement
== 2    AYoungDoctorsNotebook

--------------------
        8 new episodes


or continously play one episode after another:

dindin@laptop% turbofilm AYoungDoctorsNotebook play

Do not hesitate to ask me any questions.

-- 
Sincerely,
dindin@dindin.ru




