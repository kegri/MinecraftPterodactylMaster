config_ip = "51.83.80.95" # server IP, not url
config_port = 25565 # server port
config_command_prefix = ","
config_admin_users = [638039262952161282, 279937088219119617, 495794127682797579] # What users can use most comamands instantly
config_superadmin_users = [638039262952161282, 279937088219119617, 495794127682797579] # What users can use ALL commands
for sadmin in config_superadmin_users:
    config_admin_users.append(sadmin)
config_ping_time = 60 # How many seconds between checking the MC server
config_discord_token = "" # Bot Discord Token
config_panel_token = "" # Panel API Token
config_panel_url = "http://survivalhouse.serv.gs/" # Look in your browser URL bar for this
config_server_id = "8ac8d8bc" # Look in your browser URL bar for this, example: 025ce938
config_custom_footer = "Server: play.survival.house | 1.17.1 (Caves+Cliffs)"
config_embed_color = 0xa15600
config_votes_needed = 2
config_vote_timeout = 60 # How many seconds to wait for votes
config_server_auto_time = 5 # How many mins to check for an empty server (checks twice then shuts down)
config_shutdown_empty_server = True
config_allowed_guilds = [859144456631484466] # What discord servers the bot is allowed to take commands from.
#
config_reply_need_more_votes = "Motion: **\"{1}\"** | Votes needed: **{0}** | Use same command or use reaction to vote for motion."
config_reply_conflicting_motion = "This motion does not match the current motion. Please wait for the previous motion to expire, or vote for it."
config_reply_already_voted = "You have already voted on the current motion! Please wait for the current motion to expire or pass."
config_reply_motion_pass = 'Motion **"{0}"** passed!'
#
config_bot_source_code = "https://github.com/kegri/SurvivalHouseMaster"
