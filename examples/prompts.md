
# LLM Prompt Examples and Schemas

## System Prompt Template

```
You are an expert system administrator and shell command generator.

Your task is to convert natural language requests into safe, accurate shell commands.

Rules:
1. Always provide the most appropriate single command
2. Explain what the command does in simple terms
3. Assess risk level: low, medium, high, or critical
4. Provide 1-3 alternative approaches when applicable
5. Include warnings for potentially dangerous operations
6. Consider the user's context (OS, directory, previous commands)

Response format (JSON):
{
    "command": "shell_command_here",
    "explanation": "Clear explanation of what this does",
    "risk_level": "low|medium|high|critical",
    "confidence": 0.95,
    "alternatives": ["alt1", "alt2"],
    "warnings": ["warning1", "warning2"]
}
```

## Example Interactions

### Simple File Operations

**Input:**
```json
{
  "intent": "list all files including hidden ones",
  "context": {
    "current_directory": "/home/user/projects",
    "os_info": "Ubuntu 22.04",
    "shell": "bash"
  }
}
```

**Output:**
```json
{
  "command": "ls -la",
  "explanation": "List all files and directories including hidden ones with detailed information",
  "risk_level": "low",
  "confidence": 0.95,
  "alternatives": ["ls -a", "ls -al"],
  "warnings": []
}
```

### System Information

**Input:**
```json
{
  "intent": "check disk space usage",
  "context": {
    "current_directory": "/",
    "previous_commands": ["cd /", "ls"]
  }
}
```

**Output:**
```json
{
  "command": "df -h",
  "explanation": "Display filesystem disk space usage in human-readable format",
  "risk_level": "low",  
  "confidence": 0.9,
  "alternatives": ["du -sh /*", "df"],
  "warnings": []
}
```

### Network Operations

**Input:**
```json
{
  "intent": "download a file from a URL",
  "context": {
    "current_directory": "/home/user/downloads"
  }
}
```

**Output:**
```json
{
  "command": "curl -O <URL>",
  "explanation": "Download file from URL to current directory with original filename",
  "risk_level": "medium",
  "confidence": 0.85,
  "alternatives": ["wget <URL>", "curl -L -o filename <URL>"],
  "warnings": ["Always verify URLs before downloading", "Downloaded files should be scanned for malware"]
}
```

### High-Risk Operations

**Input:**
```json
{
  "intent": "remove all temporary files recursively",
  "context": {
    "current_directory": "/tmp"
  }
}
```

**Output:**
```json
{
  "command": "find /tmp -type f -name '*.tmp' -delete",
  "explanation": "Find and delete all .tmp files in /tmp directory",
  "risk_level": "medium",
  "confidence": 0.8,
  "alternatives": ["rm /tmp/*.tmp", "find /tmp -name '*.tmp' -exec rm {} \\;"],
  "warnings": ["This will permanently delete files", "Consider backing up important files first"]
}
```

### Critical Risk Example

**Input:**
```json
{
  "intent": "format the disk"
}
```

**Output:**
```json
{
  "command": "mkfs.ext4 /dev/sdX",
  "explanation": "Format a disk with ext4 filesystem - DESTRUCTIVE OPERATION",
  "risk_level": "critical",
  "confidence": 0.7,
  "alternatives": ["fdisk /dev/sdX", "parted /dev/sdX"],
  "warnings": [
    "THIS WILL DESTROY ALL DATA ON THE DISK",
    "Ensure you have the correct device path",
    "Backup all important data before proceeding",
    "Double-check the target device"
  ]
}
```

## Context Schema

### Request Context
```json
{
  "current_directory": "/path/to/current/dir",
  "home_directory": "/home/username", 
  "os_info": "Ubuntu 22.04.3 LTS",
  "shell": "bash",
  "user": "username",
  "previous_commands": [
    "ls -la",
    "cd projects", 
    "git status"
  ],
  "session_start": "2024-01-15T10:30:00Z"
}
```

### Response Schema
```json
{
  "command": "string - the shell command to execute",
  "explanation": "string - human-readable explanation",
  "risk_level": "enum - low|medium|high|critical", 
  "confidence": "float - 0.0 to 1.0",
  "alternatives": "array of strings - alternative commands",
  "warnings": "array of strings - safety warnings"
}
```

## Safety Patterns

### Risk Level Guidelines

**Low Risk:**
- File listing (ls, find for reading)
- Navigation (cd, pwd)
- Viewing files (cat, less, head, tail)
- Process listing (ps, top, htop)

**Medium Risk:**
- File creation/modification
- Package operations (apt install)
- Network requests (curl, wget)
- Archive operations (tar, zip)

**High Risk:**
- System configuration changes
- Permission modifications (chmod, chown)
- Process termination (kill, killall)
- Firewall changes

**Critical Risk:**
- Destructive operations (rm -rf, dd)
- Filesystem operations (mkfs, fdisk)
- System shutdown/reboot
- Security changes (passwd, sudo config)

### Pattern Examples

```bash
# Critical patterns
rm -rf /
dd if=/dev/zero of=/dev/sda
mkfs.ext4 /dev/sda1
chmod 777 /etc/passwd

# High risk patterns  
sudo rm -rf
curl <url> | bash
wget <url> | sh
chmod -R 777

# Medium risk patterns
sudo apt install
kill -9 <pid>
iptables -A INPUT
systemctl restart
```
