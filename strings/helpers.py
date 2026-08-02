# ══════════════════════════════════════════════════════════════
# ║   MuskanBot — Premium Help Strings  ✦  @MuskanBot        ║
# ══════════════════════════════════════════════════════════════


HELP_1 = """<b>╭━━〔 <emoji id=6269458311381258421>🎵</emoji><b>  ADMIN COMMANDS 〕━━╮</b>

<blockquote><b><emoji id=5388632425314140043>🎵</emoji><b> Playback Controls</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/pause</code>    ▸  Pause the current stream
<code>/resume</code>   ▸  Resume a paused stream
<code>/skip</code>     ▸  Skip to the next track
<code>/end</code>      ▸  Clear queue &amp; stop stream
<code>/stop</code>     ▸  Same as /end

<b><emoji id=5470135030393090150>🎵</emoji><b> Panel &amp; Queue</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/player</code>   ▸  Open interactive player panel
<code>/queue</code>    ▸  View all queued tracks

<b><emoji id=5264919878082509254>🎵</emoji><b> AutoPlay</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/autoplay on</code>   ▸  Enable autoplay — bot auto-plays a related YouTube track when queue ends
<code>/autoplay off</code>  ▸  Disable autoplay — bot stops when queue is empty
<code>/autoplay</code>       ▸  Check current autoplay status
<code>/cautoplay</code>      ▸  Same for linked channel

<b><emoji id=5420323339723881652>🎵</emoji><b> Bio Link Guard</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/biodetect on</code>   ▸  Auto-delete promo bio links
<code>/biodetect off</code>  ▸  Disable detection
<code>/biodetect</code>      ▸  Check current status

<i><emoji id=5774034804450267485>🎵</emoji><b> Add <b>c</b> before any command for channel use — e.g. <code>/cpause</code>  <code>/cskip</code> ❞</i></blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_2 = """<b>╭━━━〔 🛡  AUTH USERS 〕━━━╮</b>

<blockquote><i>❝ Grant admin powers to trusted users — without making them group admins. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/auth</code> <i>[username / user_id]</i>
  ▸  Add a user to the auth list

<code>/unauth</code> <i>[username / user_id]</i>
  ▸  Remove a user from the auth list

<code>/authusers</code>
  ▸  View all authorised users in this group</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_3 = """<b>╭━━━〔 📢  BROADCAST 〕━━━━╮</b>
<b>          ✦  Sudo Only</b>

<blockquote><i>❝ Reach every chat the bot serves — in one command. ❞</i>

<b>◆ Command</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/broadcast</code> <i>[message or reply]</i>
  ▸  Send a broadcast to all served chats

<b>◆ Broadcast Flags</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>-pin</code>        ▸  Pin the message silently
<code>-pinloud</code>    ▸  Pin with notification
<code>-user</code>       ▸  Send to users who started the bot
<code>-assistant</code>  ▸  Send from assistant account
<code>-nobot</code>      ▸  Skip bot broadcast

<b>◆ Example</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/broadcast -user -assistant -pin Hello everyone!</code></blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_4 = """<b>╭━━〔 🚫  CHAT BLACKLIST 〕━━╮</b>
<b>          ✦  Sudo Only</b>

<blockquote><i>❝ Keep unwanted groups out — your bot, your rules. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/blacklistchat</code> <i>[chat_id]</i>
  ▸  Block a chat from using the bot

<code>/whitelistchat</code> <i>[chat_id]</i>
  ▸  Re-allow a blacklisted chat

<code>/blacklistedchats</code>
  ▸  View all currently blacklisted chats</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_5 = """<b>╭━━━〔 🚷  BLOCK USERS 〕━━━╮</b>
<b>          ✦  Sudo Only</b>

<blockquote><i>❝ Blocked users are silenced — no commands, no access. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/block</code> <i>[username / reply]</i>
  ▸  Block a user from all bot functions

<code>/unblock</code> <i>[username / reply]</i>
  ▸  Unblock a previously blocked user

<code>/blockedusers</code>
  ▸  View the full blocked users list</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_6 = """<b>╭━━〔 📺  CHANNEL PLAY 〕━━━╮</b>

<blockquote><i>❝ Stream premium audio &amp; video directly inside your channel videochat. ❞</i>

<b>◆ Stream Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/cplay</code>       ▸  Stream audio in channel VC
<code>/cvplay</code>      ▸  Stream video in channel VC
<code>/cplayforce</code>  ▸  Force-start audio (stops current)
<code>/cvplayforce</code> ▸  Force-start video (stops current)

<b>◆ Channel Link</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/channelplay</code> <i>[username / id]</i>
  ▸  Link a channel — control it from group commands
<code>/channelplay disable</code>
  ▸  Unlink the connected channel</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_7 = """<b>╭━━━〔 🔨  GLOBAL BAN 〕━━━╮</b>
<b>          ✦  Sudo Only</b>

<blockquote><i>❝ Globally banned users are blocked across every chat the bot serves. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/gban</code> <i>[username / reply]</i>
  ▸  Globally ban a user from the bot

<code>/ungban</code> <i>[username / reply]</i>
  ▸  Lift the global ban from a user

<code>/gbannedusers</code>
  ▸  View all globally banned users</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_8 = """<b>╭━━━〔 🔁  LOOP STREAM 〕━━━╮</b>

<blockquote><i>❝ Let your favourite track play on repeat — forever if you wish. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/loop</code>
  ▸  Enable loop for the current track

<code>/loop disable</code>
  ▸  Disable loop mode

<code>/loopqueue</code>
  ▸  Loop the entire queue

<code>/loopqueue disable</code>
  ▸  Disable queue loop</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_9 = """<b>╭━━━〔 ⚙  MAINTENANCE 〕━━━╮</b>
<b>          ✦  Sudo Only</b>

<blockquote><i>❝ Keep the engine running — monitor, log, and control with ease. ❞</i>

<b>◆ Logging</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/logs</code>
  ▸  Fetch live bot logs

<code>/logger enable</code>   ▸  Start activity logging
<code>/logger disable</code>  ▸  Stop activity logging

<b>◆ Maintenance Mode</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/maintenance enable</code>   ▸  Enable maintenance mode
<code>/maintenance disable</code>  ▸  Disable maintenance mode</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_10 = """<b>╭━━〔 🏓  PING &amp; STATS 〕━━━╮</b>

<blockquote><i>❝ Real-time pulse — check if the bot is alive and performing at its best. ❞</i>

<b>◆ General</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/start</code>  ▸  Start the music bot
<code>/help</code>   ▸  Open the help menu

<b>◆ System Info</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/ping</code>   ▸  Ping &amp; show system resource stats
<code>/stats</code>  ▸  Show overall bot usage statistics</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_11 = """<b>╭━━〔 🎵  PLAY COMMANDS 〕━━╮</b>

<blockquote><i>❝ Stream anything — a song name, a YouTube link, a Spotify track. Just play. ❞</i>

<b>◆ Audio Streaming</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/play</code> <i>[song / url]</i>
  ▸  Stream the requested audio track

<code>/playforce</code> <i>[song / url]</i>
  ▸  Force-start audio (skips current stream)

<b>◆ Video Streaming</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/vplay</code> <i>[song / url]</i>
  ▸  Stream the requested video track

<code>/vplayforce</code> <i>[song / url]</i>
  ▸  Force-start video (skips current stream)

<i>❝ Add <b>c</b> prefix for channel streaming — <code>/cplay</code>  <code>/cvplay</code> ❞</i></blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_12 = """<b>╭━━━〔 🎙  VC NOTIFIER 〕━━━╮</b>

<blockquote><i>❝ Never miss a moment — know exactly who enters or exits the voice chat. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/vclogger on</code>   ▸  Enable VC join/leave alerts
<code>/vclogger off</code>  ▸  Disable VC notifications
<code>/vclogger</code>      ▸  Check current status

<b>◆ Behaviour</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
▸  Activates on every group message when enabled
▸  Notification messages auto-delete after <b>10 seconds</b></blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_13 = """<b>╭━━━〔 ⏩  SEEK STREAM 〕━━━╮</b>

<blockquote><i>❝ Jump to any moment in the track — forward or back, in seconds. ❞</i>

<b>◆ Commands</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/seek</code> <i>[seconds]</i>
  ▸  Seek forward to the given position

<code>/seekback</code> <i>[seconds]</i>
  ▸  Seek backward to the given position</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_14 = """<b>╭━━〔 ⬇  SONG DOWNLOAD 〕━━╮</b>

<blockquote><i>❝ Save the vibe — download any track directly from YouTube, fast. ❞</i>

<b>◆ Command</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/song</code> <i>[song name / YouTube URL]</i>
  ▸  Download in <b>MP3</b> or <b>MP4</b> format
  ▸  File sent directly to chat — instant delivery</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""


HELP_15 = """<b>╭━━〔 ⚡  SPEED CONTROL 〕━━╮</b>
<b>          ✦  Admins Only</b>

<blockquote><i>❝ Slow it down to savour every note, or crank it up to match your vibe. ❞</i>

<b>◆ Group Playback</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/speed</code>     ▸  Adjust audio speed in group
<code>/playback</code>  ▸  Same as /speed

<b>◆ Channel Playback</b>
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
<code>/cspeed</code>    ▸  Adjust audio speed in channel
<code>/cplayback</code> ▸  Same as /cspeed</blockquote>

<b>╰━━━━━━━━━━━━━━━━━━━━━━━━╯</b>"""
