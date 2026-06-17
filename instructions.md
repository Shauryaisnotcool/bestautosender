# Discord Automation Bot Instructions

This bot is optimized for **Render.com** hosting and **UptimeRobot** monitoring. It performs two independent tasks using your personal Discord Token.

## 🚀 Features
1. **Server Auto-Sender**: Sends the text in `msg.txt` to a specific Channel ID every 65 seconds.
2. **Auto DM Responder**: Checks for new DM requests every 30 seconds and automatically replies with a specific invite link: `https://discord.gg/9mGBcb4kZd`.
3. **Keep-Alive Web Server**: Provides a lightweight endpoint for UptimeRobot to prevent the bot from sleeping.

---

## 🛠️ Configuration (Render.com)

Since Render does not use your local `.env` file, you **must** add these "Environment Variables" in the Render Dashboard:

1. **`DISCORD_AUTH_TOKEN`**: Your personal Discord account token.
2. **`DISCORD_CHANNEL_ID`**: The ID of the channel where the bot should send messages.
3. **`PORT`**: (Optional) Render sets this automatically.

### How to get your Channel ID:
- Enable **Developer Mode** in Discord (User Settings > Advanced).
- Right-click the channel name and select **Copy Channel ID**.

---

## 📂 File Structure
- `main.py`: The core logic (Server Sender + DM Responder).
- `msg.txt`: Put your advertisement text here.
- `requirements.txt`: Libraries needed (`requests`, `flask`, `python-dotenv`, `gunicorn`).
- `Procfile`: Instructions for Render to start the bot.

---

## 📝 Monitoring
To see if the bot is working:
1. Go to your **Render Dashboard**.
2. Click on your project and go to the **Logs** tab.
3. You will see:
   - `SERVER: Message sent successfully.`
   - `DM: Replied to user in channel ...`

---

## ⚠️ Important Notes
- **Rate Limits**: If you see `Rate limited` in the logs, the bot will automatically wait and retry. Do not lower the 65-second interval to avoid being banned.
- **DM Responder**: It checks for the last message in a DM. If the last message was from the other person, it sends the link. It will not spam the same person if the last message was already your link.
