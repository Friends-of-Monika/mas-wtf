<h1 align="center">🔍 Where is That From</h1>
<h3 align="center">Easily find out what submod owns a topic!</h3>
<h5 align="center">Yes, it abbreviates to WTF.</h5>

<p align="center">
  <a href="https://github.com/friends-of-monika/mas-wtf/releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/friends-of-monika/mas-wtf">
  </a>
  <a href="https://github.com/friends-of-monika/mas-wtf/releases">
    <img alt="Release downloads" src="https://img.shields.io/github/downloads/friends-of-monika/mas-wtf/total">
  </a>
  <a href="https://github.com/friends-of-monika/mas-wtf/blob/main/LICENSE.txt">
    <img alt="MIT license badge" src="https://img.shields.io/badge/License-MIT-lightgrey.svg">
  </a>
  <a href="https://dcache.me/discord">
    <img alt="Discord server" src="https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=shield">
  </a>
  <a href="https://ko-fi.com/Y8Y15BC52">
    <img alt="Ko-fi badge" src="https://ko-fi.com/img/githubbutton_sm.svg" height="20">
  </a>
</p>


## 🌟 Features

A true must-have for everyone eager to try out new submods and those who have a
ton of them and might need help finding where a certain topic comes from!~

* Tells apart official topics and submod topics
* Provides information on what the current topic name is
* Displays owning submod name and script file location

## ❓ Installing

1. Go to [the latest release page][6] and scroll to Assets section.
2. Download `where-is-that-from-VERSION.zip` file.
3. Drag and drop `Submods` folder from it into your `game` folder.
4. You're all set!~

### 📚 How to use?

Whenever you need to find out where is the topic you're currently going through
is located and what submod owns it, press the `W` key or `?` (question mark,
might require holding down `Shift ⬆` key) and the popup dialog window will tell
you all the available info.

### 🙋 FAQ

*Long story short, blame Ren'Py. Not MAS, not MAS developers, not WTF
developers, blame Ren'Py for its poor design choices.*

#### 🤔 Why does it say 'seems' and 'might'? Why so uncertain?

Unfortunately, there isn't a reliable straightforward way to programmatically
tell which file is *exactly* being used by Ren'Py right now for showing a
certain topic; to somehow make do with that, Where is That From submod does a
few tricks that aren't always reliable not are always accurate.

In addition to that, there is no way to know for sure that current topic will
be accessible once you finish it, as it might perform some locking logic at the
end and there is not way to tell if it definitely will be accessible again with
confidence. Sorry for the uncertainty, but it can only do so much...

#### 🤔 Why does it not detect the submod owning a topic?

Due to how Ren'Py works and how MAS handles events, there is no way to really
tell for sure if some topic belongs to a file with some submod metadata in it.
Where is That From submod tries to search for submod metadata in current topic
file, and if there was none, it could also try to look around in neighboring
files, however, in cases when .RPY/.RPYC file is placed right in `game` or
`game/Submods` and not in its own folder, the search area is too broad and it
cannot look around to find submod header and tell for sure without a high risk
of getting a false positive.

Alternatively, it could be that submod just doesn't have a submod header. Submod
developers may omit that bit for their own reasons, which prevents Where is That
From submod from determining what submod is the script file provided by. But, it
can at least tell what file contains the topic you're currently looking at.

## 💬 Join our Discord

We're up to chat! Come join submod author's Discord server [here][8].

[![Discord server invitation][10]][8]

[6]: https://github.com/friends-of-monika/mas-wtf/releases/latest
[8]: https://dcache.me/discord
[9]: https://mon.icu/discord
[10]: https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=banner3
[12]: https://github.com/friends-of-monika/mas-wtf
