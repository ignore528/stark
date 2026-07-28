
# ======================================================================
# ||   MuskanBot — Muskan_Music Help Strings                       ||
# ======================================================================


HELP_1 = """<b>╔══〔 ⚙ ADMIN COMMANDS 〕══╗</b>

<blockquote><b>◈ Playback Controls</b>
<code>/pause</code>    ▸  Pause the current stream
<code>/resume</code>   ▸  Resume a paused stream
<code>/skip</code>     ▸  Skip to next track in queue
<code>/end</code>      ▸  Clear queue &amp; stop stream
<code>/stop</code>     ▸  Same as /end

<b>◈ Panel &amp; Queue</b>
<code>/player</code>   ▸  Open interactive player panel
<code>/queue</code>    ▸  Show queued tracks list

<b>◈ Bio Link Guard</b>
<code>/biodetect on</code>   ▸  Auto-delete msgs from users with promo links in bio
<code>/biodetect off</code>  ▸  Disable bio link detection
<code>/biodetect</code>      ▸  Check current status

<b>⌖</b>  Add <b>c</b> prefix to any command for channel use
     e.g.  <code>/cpause</code>  <code>/cresume</code>  <code>/cskip</code></blockquote>

<b>╚════════════════════════╝</b>"""


HELP_2 = """<b>╔══〔 ◆ AUTH USERS 〕══╗</b>

<blockquote>Auth users can use admin rights without being a group admin.

<b>◈ Commands</b>
<code>/auth</code> <i>[username / user_id]</i>
  ▸  Add a user to the auth list

<code>/unauth</code> <i>[username / user_id]</i>
  ▸  Remove a user from the auth list

<code>/authusers</code>
  ▸  View all authorised users of this group</blockquote>

<b>╚═══════════════════════╝</b>"""


HELP_3 = """<b>╔══〔 ✦ BROADCAST 〕══╗</b>
<b>         ⌖  Sudo only</b>

<blockquote><code>/broadcast</code> <i>[message / reply]</i>
  ▸  Broadcast a message to all served chats

<b>◈ Broadcast Flags</b>
<code>-pin</code>        ▸  Pin the message silently
<code>-pinloud</code>    ▸  Pin with notification
<code>-user</code>       ▸  Send to users who started the bot
<code>-assistant</code>  ▸  Send from assistant account
<code>-nobot</code>      ▸  Force skip bot broadcast

<b>◈ Example</b>
<code>/broadcast -user -assistant -pin Hello everyone!</code></blockquote>

<b>╚══════════════════════╝</b>"""


HELP_4 = """<b>╔══〔 ⊘ CHAT BLACKLIST 〕══╗</b>
<b>           ⌖  Sudo only</b>

<blockquote>Block unwanted chats from using the bot.

<b>◈ Commands</b>
<code>/blacklistchat</code> <i>[chat_id]</i>
  ▸  Blacklist a chat from using the bot

<code>/whitelistchat</code> <i>[chat_id]</i>
  ▸  Whitelist a previously blacklisted chat

<code>/blacklistedchats</code>
  ▸  View all blacklisted chats</blockquote>

<b>╚════════════════════════╝</b>"""


HELP_5 = """<b>╔══〔 ⊗ BLOCK USERS 〕══╗</b>
<b>         ⌖  Sudo only</b>

<blockquote>Ignore blocked users — they cannot use any bot commands.

<b>◈ Commands</b>
<code>/block</code> <i>[username / reply]</i>
  ▸  Block a user from the bot

<code>/unblock</code> <i>[username / reply]</i>
  ▸  Unblock a blocked user

<code>/blockedusers</code>
  ▸  View all blocked users</blockquote>

<b>╚═══════════════════════╝</b>"""


HELP_6 = """<b>╔══〔 ◉ CHANNEL PLAY 〕══╗</b>

<blockquote>Stream audio or video directly in a channel videochat.

<b>◈ Stream Commands</b>
<code>/cplay</code>       ▸  Stream audio in channel videochat
<code>/cvplay</code>      ▸  Stream video in channel videochat
<code>/cplayforce</code>  ▸  Force-start audio (stops current stream)
<code>/cvplayforce</code> ▸  Force-start video (stops current stream)

<b>◈ Channel Link</b>
<code>/channelplay</code> <i>[username / id]</i>
  ▸  Link channel to group — control via group commands
<code>/channelplay disable</code>
  ▸  Unlink the connected channel</blockquote>

<b>╚═════════════════════════╝</b>"""


HELP_7 = """<b>╔══〔 ⛒ GLOBAL BAN 〕══╗</b>
<b>        ⌖  Sudo only</b>

<blockquote>Globally ban users across all served chats.

<b>◈ Commands</b>
<code>/gban</code> <i>[username / reply]</i>
  ▸  Ban user from all served chats &amp; blacklist from bot

<code>/ungban</code> <i>[username / reply]</i>
  ▸  Lift the global ban

<code>/gbannedusers</code>
  ▸  View all globally banned users</blockquote>

<b>╚══════════════════════╝</b>"""


HELP_8 = """<b>╔══〔 ↺ LOOP STREAM 〕══╗</b>

<blockquote>Repeat the current stream on loop.

<b>◈ Commands</b>
<code>/loop enable</code>   ▸  Enable loop mode
<code>/loop disable</code>  ▸  Disable loop mode
<code>/loop</code> <i>[1, 2, 3 ...]</i>
  ▸  Loop for an exact number of times</blockquote>

<b>╚═══════════════════════╝</b>"""


HELP_9 = """<b>╔══〔 ⌧ MAINTENANCE 〕══╗</b>
<b>       ⌖  Sudo only</b>

<blockquote><b>◈ Logging</b>
<code>/logs</code>
  ▸  Fetch live bot logs

<code>/logger enable</code>   ▸  Start activity logging
<code>/logger disable</code>  ▸  Stop activity logging

<b>◈ Maintenance Mode</b>
<code>/maintenance enable</code>   ▸  Enable maintenance mode
<code>/maintenance disable</code>  ▸  Disable maintenance mode</blockquote>

<b>╚══════════════════════╝</b>"""


HELP_10 = """<b>╔══〔 ◎ PING &amp; STATS 〕══╗</b>

<blockquote><b>◈ General</b>
<code>/start</code>  ▸  Start the music bot
<code>/help</code>   ▸  Open the help menu

<b>◈ System Info</b>
<code>/ping</code>   ▸  Show ping &amp; system resource stats
<code>/stats</code>  ▸  Show overall bot usage statistics</blockquote>

<b>╚═════════════════════════╝</b>"""


HELP_11 = """<b>╔══〔 ▷ PLAY COMMANDS 〕══╗</b>

<blockquote><b>◈ Audio Streaming</b>
<code>/play</code> <i>[song / url]</i>
  ▸  Stream the requested audio track

<code>/playforce</code> <i>[song / url]</i>
  ▸  Force-start audio (skips current stream)

<b>◈ Video Streaming</b>
<code>/vplay</code> <i>[song / url]</i>
  ▸  Stream the requested video track

<code>/vplayforce</code> <i>[song / url]</i>
  ▸  Force-start video (skips current stream)

<b>⌖</b>  Prefix <b>c</b> to any command for channel streaming
     e.g.  <code>/cplay</code>  <code>/cvplay</code></blockquote>

<b>╚════════════════════════╝</b>"""


HELP_12 = """<b>╔══〔 ⟡ VC NOTIFIER 〕══╗</b>

<blockquote>Get notified whenever someone joins or leaves the voice chat.

<b>◈ Commands</b>
<code>/vclogger on</code>   ▸  Enable VC join/leave notifications
<code>/vclogger off</code>  ▸  Disable VC notifications
<code>/vclogger</code>      ▸  Check current status

<b>◈ Behaviour</b>
▸  Auto-activates on every group message when enabled
▸  Notification messages auto-delete after <b>10 seconds</b></blockquote>

<b>╚══════════════════════╝</b>"""


HELP_13 = """<b>╔══〔 ⇢ SEEK STREAM 〕══╗</b>

<blockquote>Jump to any position in the ongoing stream.

<b>◈ Commands</b>
<code>/seek</code> <i>[seconds]</i>
  ▸  Seek forward to the given position

<code>/seekback</code> <i>[seconds]</i>
  ▸  Seek backward to the given position</blockquote>

<b>╚══════════════════════╝</b>"""


HELP_14 = """<b>╔══〔 ⬇ SONG DOWNLOAD 〕══╗</b>

<blockquote>Download any track directly from YouTube.

<b>◈ Command</b>
<code>/song</code> <i>[song name / YouTube URL]</i>
  ▸  Download in <b>MP3</b> or <b>MP4</b> format
  ▸  Bot sends file directly to chat</blockquote>

<b>╚══════════════════════════╝</b>"""


HELP_15 = """<b>╔══〔 ≋ SPEED CONTROL 〕══╗</b>
<b>         ⌖  Admins only</b>

<blockquote>Control the playback speed of the ongoing stream.

<b>◈ Group Playback</b>
<code>/speed</code>     ▸  Adjust audio speed in group
<code>/playback</code>  ▸  Same as /speed

<b>◈ Channel Playback</b>
<code>/cspeed</code>    ▸  Adjust audio speed in channel
<code>/cplayback</code> ▸  Same as /cspeed</blockquote>

<b>╚═════════════════════════╝</b>"""
