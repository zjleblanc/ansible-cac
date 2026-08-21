# Setting Environment Variables for Cursor - Mac

The cursor MCP configuration file `~/.cursor/mcp.json` supports environment variables via the format: `${env:VAR}`. I recommend using this capability to avoid hardcoding secrets (your AAP token) in a configuration file.

The challenge becomes, how do we enable Cursor to load the appropriate environment variables at launch? Manually sourcing a `.env` file each time we open Cursor is not ideal.

## ~/Library/LaunchAgents/com.user.setenv.plist

On a Mac, we can leverage a plist to configure launchctl (the app launching service) to load desired environment variables. Below is an example plist file, which automatically loads MCP env vars anytime Cursor is opened:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.setenv</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/launchctl</string>
        <string>setenv</string>
        <string>AAP_HOST</string>
        <string>aap.example.com</string>
        <string>/bin/launchctl</string>
        <string>setenv</string>
        <string>AAP_MCP_PORT</string>
        <string>8448</string>
        <string>/bin/launchctl</string>
        <string>setenv</string>
        <string>AAP_TOKEN</string>
        <string>secret</string>
        <string>/bin/launchctl</string>
        <string>setenv</string>
        <!-- OPTIONAL - support for self-signed certs -->
        <string>NODE_TLS_REJECT_UNAUTHORIZED</string>
        <string>0</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
``