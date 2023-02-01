# Email Updater

A script to automate sending emails

- Pulls sender and receiver credentials from `.env` file
- Password stored should be hashed in base64
- Can be used as a cron job

```
0 18 * * Mon-Fri /path/to/venv/bin/python /path/to/updater.py >> /path/to/cronjob.logs 2>&1
```

- Use bash alias for easy editing of email body

```
alias eup="/usr/bin/nvim \$HOME/path/to/daily_updates/\$(date -d \"\$([[ \$(date -d '+6 hours' +%u) -gt 5 ]] && echo 'next Monday' || echo '+6 hours')\" '+%Y-%m-%d').txt"
```

> The cron job above sends email at 6pm on every working day.
> The bash alias above opens the file for next working day if called after 6pm.
