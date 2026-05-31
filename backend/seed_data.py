SEED_RECORDS = [
    # Category: Account & Authentication (1-10)
    {
        "question": "How can I reset my account password?",
        "answer": "Click 'Forgot Password' on the login screen, enter your email address, and follow the instructions sent to your inbox to set a new password."
    },
    {
        "question": "Does the app support Multi-Factor Authentication (MFA)?",
        "answer": "Yes, you can enable Multi-Factor Authentication (MFA) in your Account Settings under the Security tab. We support Google Authenticator, Authy, and SMS."
    },
    {
        "question": "How can I delete my account permanently?",
        "answer": "To permanently delete your account, navigate to Settings > Profile > Account Settings and scroll down to 'Delete Account'. This action is irreversible."
    },
    {
        "question": "Can I merge two separate accounts under different emails?",
        "answer": "Account merging is not supported automatically. Please submit a request to support with both email addresses, and we will migrate your data manually."
    },
    {
        "question": "How do I change my primary account email address?",
        "answer": "Navigate to Settings > Profile > Account Settings, click on the 'Email Address' field, enter your new email, and verify it using the confirmation link sent to the new address."
    },
    {
        "question": "Why did my account get locked out?",
        "answer": "Your account is temporarily locked for 15 minutes after 5 consecutive failed login attempts. You can wait for the lockout to expire or click 'Forgot Password' to reset it immediately."
    },
    {
        "question": "Can I see active sessions and log out of other devices?",
        "answer": "Yes, under Settings > Security, there is an 'Active Sessions' list. You can review all logged-in devices and click 'Terminate Session' next to any device, or 'Log Out of All Devices'."
    },
    {
        "question": "What happens to my data if my account is inactive?",
        "answer": "Accounts that are inactive for 12 consecutive months are flagged for deletion. We send email warnings 30, 15, and 7 days prior to any data purge."
    },
    {
        "question": "How do I update my profile avatar photo?",
        "answer": "Go to Settings > Profile, click on your current avatar placeholder, upload a PNG or JPEG file (up to 5MB), crop it if necessary, and click 'Save Changes'."
    },
    {
        "question": "Does your platform support Single Sign-On (SSO)?",
        "answer": "Yes, Single Sign-On (SSO) via SAML 2.0 and OIDC is available for Enterprise workspaces. You can configure it in the Admin Settings panel under Identity & Access."
    },

    # Category: Billing & Subscriptions (11-20)
    {
        "question": "What is your subscription refund policy?",
        "answer": "We offer a full refund within 14 days of purchase for both monthly and annual subscriptions. To request a refund, please contact billing support."
    },
    {
        "question": "How do I cancel my paid subscription?",
        "answer": "Go to Settings > Billing & Workspace Subscription, click on 'Manage Plan', and select 'Cancel Subscription' at the bottom of the portal."
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept major credit cards (Visa, MasterCard, American Express, Discover), PayPal, Apple Pay, Google Pay, and wire transfers for Enterprise contracts."
    },
    {
        "question": "Why did my subscription renewal payment fail?",
        "answer": "Renewal payments typically fail due to expired credit cards, insufficient funds, or bank security blocks. You can update your payment details under Settings > Billing."
    },
    {
        "question": "Where can I download my billing invoices?",
        "answer": "Invoices are available under Settings > Billing > Invoice History. You can view, download, or email PDF versions of all past receipts."
    },
    {
        "question": "Do you offer discounts for educational institutions or non-profits?",
        "answer": "Yes, we offer a 50% discount for registered non-profit organizations and accredited educational institutions. Apply through our community discount form."
    },
    {
        "question": "Can I upgrade my plan in the middle of a billing cycle?",
        "answer": "Yes, you can upgrade at any time. The system will calculate a prorated amount for the remaining days of your billing cycle and charge you the difference."
    },
    {
        "question": "What is the difference between the Free and Pro plan?",
        "answer": "The Pro plan unlocks unlimited workspaces, advanced integrations, custom fields, Gantt charts, priority support, and increases file storage from 5GB to 100GB."
    },
    {
        "question": "Will I be charged tax on my subscription?",
        "answer": "Tax is charged based on your location and billing address. In the US, state sales tax applies where applicable. In the EU, VAT is charged unless a valid VAT ID is provided."
    },
    {
        "question": "How do I update my credit card details?",
        "answer": "Go to Settings > Billing, click on 'Update Payment Method', enter your card number, expiration date, and CVV code, then click 'Update'."
    },

    # Category: UI & Customization (21-30)
    {
        "question": "How do I enable dark mode?",
        "answer": "Click on your profile avatar in the top right corner, select 'Theme Preferences', and toggle the setting to 'Dark Mode'."
    },
    {
        "question": "Can I change the sidebar width or collapse it?",
        "answer": "Yes, you can collapse the left sidebar by clicking the '<' icon at the bottom of the sidebar or pressing 'Ctrl + /'. You can resize it by dragging its right edge."
    },
    {
        "question": "How do I change the display language?",
        "answer": "Go to Settings > Preferences > Language & Region, select your preferred language from the dropdown menu, and click 'Apply Language'."
    },
    {
        "question": "How do I customize dashboard widgets?",
        "answer": "Click on 'Customize Dashboard' in the top right corner, drag and drop widgets to rearrange them, click the '+' icon to add widgets, or 'x' to remove widgets."
    },
    {
        "question": "Is it possible to disable UI animations?",
        "answer": "Yes, navigate to Settings > Accessibility and turn on 'Reduce Motion' to disable transitions, fades, and structural hover animations."
    },
    {
        "question": "Can I set a custom background image for my workspace?",
        "answer": "Yes, go to Workspace Settings > Appearance, upload a high-resolution image under 'Custom Background', and click 'Apply'."
    },
    {
        "question": "How do I increase the font size in the app?",
        "answer": "Go to Settings > Accessibility, and adjust the 'Text Scaling' slider. We support scaling options from 80% to 150% of the default font size."
    },
    {
        "question": "Can I hide completed tasks from my dashboard list?",
        "answer": "Yes, click on the 'Filter' dropdown menu at the top of your task list and uncheck the 'Show Completed Tasks' option."
    },
    {
        "question": "How do I change the start day of the week on the calendar?",
        "answer": "Go to Settings > Preferences > Calendar, and select either 'Sunday' or 'Monday' from the 'Week Starts On' dropdown selection."
    },
    {
        "question": "Why is the billing dashboard showing a blank screen?",
        "answer": "This is typically caused by active ad-blockers blocking our payment gateway scripts (Stripe). Please temporarily disable ad-blockers and refresh the page."
    },

    # Category: Tasks & Projects (31-40)
    {
        "question": "How do I create a new project template?",
        "answer": "Configure a project with your tasks, columns, and settings. Then, click on the project dropdown header and select 'Save Project as Template'."
    },
    {
        "question": "Can I set recurring deadlines for tasks?",
        "answer": "Yes, open a task, click on 'Due Date', toggle 'Set Recurring', and choose the frequency (daily, weekly, monthly) and repeat intervals."
    },
    {
        "question": "How do task dependencies work?",
        "answer": "Open a task, click 'Dependencies', and choose 'Blocker' or 'Blocked By' relative to another task. Gantt charts will auto-align dates if blocker dates shift."
    },
    {
        "question": "How do I archive an completed project?",
        "answer": "Click on the three dots next to the project name in the sidebar, select 'Archive Project', and confirm. You can restore it anytime from Workspace Settings > Archived Projects."
    },
    {
        "question": "What is the maximum file attachment size?",
        "answer": "For Free plan users, the maximum file attachment size is 25MB per file. Pro and Enterprise plans support file uploads up to 5GB."
    },
    {
        "question": "Can I create custom fields for my tasks?",
        "answer": "Yes, click the '+' sign in the task table column headers or 'Customize Fields' in a task card. You can create text, number, dropdown, checkbox, and date fields."
    },
    {
        "question": "How do I assign a single task to multiple users?",
        "answer": "Open the task card, click the 'Assignee' area, and select multiple members. Note: Multi-assignee support must be turned on in Workspace Settings > Task Rules."
    },
    {
        "question": "What are project milestones and how do I create them?",
        "answer": "Milestones represent key checkpoints. Open a task, check 'Convert to Milestone' in the task options. Milestones show as diamonds on your Gantt chart."
    },
    {
        "question": "How do I track time spent on a task?",
        "answer": "Open a task, click the play button next to 'Time Tracker' to start a timer, or click 'Log Time' to manually input hours and minutes."
    },
    {
        "question": "How can I restore a deleted task?",
        "answer": "Go to Workspace Settings > Trash, find your task in the recently deleted list (retained for 30 days), and click 'Restore'."
    },

    # Category: Notifications & Alerts (41-50)
    {
        "question": "How do I configure email notification preferences?",
        "answer": "Navigate to Settings > Notifications, and toggle checkboxes under the 'Email Notifications' column for specific triggers like mentions or updates."
    },
    {
        "question": "Why am I not receiving desktop push notifications?",
        "answer": "Ensure browser permission is granted. Go to browser settings, click the lock icon next to the URL, and ensure Notifications are set to 'Allow'. Also enable it in app Settings."
    },
    {
        "question": "Can I receive notifications in Slack?",
        "answer": "Yes, by integrating Slack. Under Settings > Integrations, connect Slack and map specific project alerts to desired Slack channels."
    },
    {
        "question": "How do I turn on Do Not Disturb (DND) mode?",
        "answer": "Click on your profile avatar, select 'Snooze Notifications', and select a duration (30 mins, 2 hours, 8 hours, or custom schedule)."
    },
    {
        "question": "Why am I getting too many spam emails from the app?",
        "answer": "You are likely subscribed to 'Daily Workspace Digests' and 'All Activity'. Go to Settings > Notifications and change your email digest to 'Weekly' or 'Mentions Only'."
    },
    {
        "question": "Can I get SMS alerts for high-priority tasks?",
        "answer": "Yes, Pro and Enterprise users can add a phone number under Settings > Notifications > SMS Alerts and enable SMS for urgent priority deadlines."
    },
    {
        "question": "How do I disable notifications for a specific project?",
        "answer": "Open the project, click the bell icon in the top right header, and select 'Mute Notifications'. You will still be notified if you are directly @mentioned."
    },
    {
        "question": "Why are my mobile app notifications delayed?",
        "answer": "This is often due to background battery optimization on Android/iOS. Ensure background data usage is enabled and battery saver is disabled for our app."
    },
    {
        "question": "How do I send a direct notification to a team member?",
        "answer": "Simply mention them by typing '@username' in any task comment, description, or project chat. They will be alerted instantly based on their preferences."
    },
    {
        "question": "Can I customize the notification sound?",
        "answer": "Yes, under Settings > Notifications > Sounds, you can choose from five different sound profiles or choose 'Silent' for quiet push popups."
    },

    # Category: Integrations & API (51-60)
    {
        "question": "What are the API rate limits?",
        "answer": "Our standard API rate limit is 100 requests per minute per API key. If you exceed this limit, you will receive a HTTP 429 Too Many Requests response."
    },
    {
        "question": "How do I set up webhooks?",
        "answer": "Go to the Developer Console, click on 'Webhooks', select 'Add Webhook', and enter your payload URL and the events you want to listen to."
    },
    {
        "question": "How do I generate a new API key?",
        "answer": "Navigate to settings, select 'Developer Settings', click 'Generate New Key', select the scopes needed, and copy the key immediately as it won't be shown again."
    },
    {
        "question": "Does the system integrate with GitHub?",
        "answer": "Yes! Go to Settings > Integrations, select 'GitHub', and authorize the app. You can link commits to tasks by referencing task IDs like '#TSK-123' in commit messages."
    },
    {
        "question": "How do I connect Slack to my workspace?",
        "answer": "Go to Settings > Integrations > Slack, click 'Install Slack App', authorize access to your workspace, and select the channels for project updates."
    },
    {
        "question": "Can I connect Jira projects to this platform?",
        "answer": "Yes, we offer a two-way sync with Jira. Navigate to Settings > Integrations, select 'Jira Cloud', and input your Jira site URL and API token."
    },
    {
        "question": "Do you support OAuth2 authentication for custom scripts?",
        "answer": "Yes, developers can create OAuth2 applications in the Developer Console to request authorization codes and access tokens on behalf of users."
    },
    {
        "question": "How do I resolve integration sync conflicts?",
        "answer": "Sync conflicts occur if records change in both apps simultaneously. By default, 'Last Write Wins' applies, but you can configure override rules in Integration Settings."
    },
    {
        "question": "What formats does the Webhook payload support?",
        "answer": "Currently, we only support JSON formatted webhook payloads. The structure contains event type, timestamp, sender details, and full object payload."
    },
    {
        "question": "Is there a Zapier integration?",
        "answer": "Yes, search for 'WorkSync' on Zapier. You can trigger zaps when tasks are created/updated, or create tasks from other app triggers."
    },

    # Category: Mobile & Tablet (61-70)
    {
        "question": "Does the mobile app support offline editing?",
        "answer": "Yes, you can edit and create tasks offline. Changes are saved locally and synced automatically once an internet connection is re-established."
    },
    {
        "question": "How do I install the PWA on my phone?",
        "answer": "Open the web app in Chrome on Android or Safari on iOS. Tap the browser options menu (or Share button) and select 'Add to Home Screen'."
    },
    {
        "question": "Is there a native iPad or tablet app?",
        "answer": "Yes, our iOS and Android apps are fully optimized with split-pane layouts for tablets. Download them from the Apple App Store or Google Play Store."
    },
    {
        "question": "Why is the mobile app consuming too much battery?",
        "answer": "This can happen if real-time web sockets remain open in the background. Update the app to version 4.2+ which optimizes background socket pooling."
    },
    {
        "question": "How do I sync mobile calendar to Apple Calendar?",
        "answer": "Go to Settings > Calendar Sync on mobile, click 'Generate iCal Link', copy it, and paste it into Apple Calendar > Add Subscription Calendar."
    },
    {
        "question": "Does the mobile app support face ID login?",
        "answer": "Yes, iOS and Android versions support biometric login (Face ID, Touch ID, Fingerprint). Turn it on under Mobile settings > Security."
    },
    {
        "question": "Why are attachments not downloading on mobile?",
        "answer": "Ensure the app has storage permissions. Check your mobile OS settings > Apps > WorkSync > Permissions and verify Storage access is allowed."
    },
    {
        "question": "Can I use mobile widgets on iOS?",
        "answer": "Yes, we support both small and medium iOS widgets. Long press on home screen, tap '+', search for our widget, and choose your favorite layout."
    },
    {
        "question": "How do I clear mobile app cache?",
        "answer": "Go to Mobile settings > Storage > Clear Cache. This clears locally cached assets and forces a fresh sync without logging you out."
    },
    {
        "question": "Does the mobile app support scan documents?",
        "answer": "Yes, tap the '+' attachment button on a task, select 'Scan Document', use your camera to take a photo, and the app will auto-align and attach a clean PDF."
    },

    # Category: Collaboration & Sharing (71-80)
    {
        "question": "How do I invite team members to my organization?",
        "answer": "Go to Organization Settings, click on the 'Members' tab, select 'Invite Member', enter their email address, select their role, and click 'Send Invite'."
    },
    {
        "question": "How do I assign permissions to guest accounts?",
        "answer": "Guests can only view projects they are explicitly invited to. You can restrict their permissions to 'Comment Only' or 'Read-Only' in Project Member Settings."
    },
    {
        "question": "Can I share a read-only link to a project board?",
        "answer": "Yes, open the project settings, click 'Public Sharing', toggle 'Enable Public Link', and copy the URL. Anyone with this link can view the board."
    },
    {
        "question": "How do @mentions work in task comments?",
        "answer": "Type '@' followed by the name of a team member in any task comment. They will receive an email and in-app notification linking to the task."
    },
    {
        "question": "Can multiple people edit the same task description simultaneously?",
        "answer": "Yes, task descriptions support real-time collaborative editing. You will see colored cursor indicators showing where other team members are typing."
    },
    {
        "question": "How do I restrict project visibility to specific members?",
        "answer": "In Project Settings, change the visibility from 'Public to Workspace' to 'Private'. Only members explicitly added will be able to see the project."
    },
    {
        "question": "Can I transfer ownership of a workspace to someone else?",
        "answer": "Yes, navigate to Settings > Workspace settings > Billing/Ownership, click 'Transfer Ownership', enter the email of the new owner, and confirm."
    },
    {
        "question": "How do I create a team group for mentions?",
        "answer": "Go to Workspace Settings > Teams, click 'Create Team', name it (e.g. @marketing), add members, and you can now mention the entire team at once."
    },
    {
        "question": "Can we chat in real-time within the platform?",
        "answer": "Yes, we offer Project Chat rooms. Click on the chat icon in the project header to open a real-time discussion sidebar for your team."
    },
    {
        "question": "How do I comment on a specific change in the task activity log?",
        "answer": "In the task activity stream, hover over a log entry (e.g. status change) and click 'Reply' to start a nested thread relative to that change."
    },

    # Category: Data Import/Export (81-90)
    {
        "question": "How can I export my account data?",
        "answer": "You can export all workspace data as a CSV or JSON file from the Workspace settings page under the 'Export Data' section."
    },
    {
        "question": "What format should the CSV task import file be in?",
        "answer": "The CSV import file must contain headers for 'Title', 'Description', 'Due Date', and 'Assignee'. You can download our sample CSV template on the import page."
    },
    {
        "question": "How do I set up automated data backups?",
        "answer": "Enterprise plan users can enable daily automated backups under Settings > Data Management. Backups can be synced to Amazon S3 or Google Drive."
    },
    {
        "question": "Is my data encrypted?",
        "answer": "All customer data is encrypted in transit using TLS 1.3 and at rest using AES-256 encryption. We also maintain SOC 2 Type II compliance."
    },
    {
        "question": "What is our workspace storage limit?",
        "answer": "Free plans have a limit of 5GB. Pro plans support 100GB, and Enterprise plans offer 1TB of storage, with options to purchase additional blocks."
    },
    {
        "question": "How do I clear storage if limit is reached?",
        "answer": "Go to Workspace settings > Storage Analyzer. You can sort files by size, delete old attachments, or upgrade your plan to increase limit."
    },
    {
        "question": "Can I export Gantt charts as PDF?",
        "answer": "Yes, click the export icon in the Gantt chart view, select 'Export PDF', configure orientation (landscape recommended), and click 'Download'."
    },
    {
        "question": "How do I restore data from a backup?",
        "answer": "Workspace owners can upload a previously exported JSON backup file under Settings > Data Management > Restore. This overwrites current workspace data."
    },
    {
        "question": "Are deleted files permanently deleted?",
        "answer": "No, deleted files go to Workspace trash for 30 days. After 30 days, they are permanently purged from our servers and cannot be recovered."
    },
    {
        "question": "How do I download all attachments at once?",
        "answer": "Navigate to Settings > Storage, select the checkboxes for the folders or files you need, and click 'Bulk Download' to generate a ZIP archive."
    },

    # Category: Performance & Security (91-100)
    {
        "question": "How is customer data secured?",
        "answer": "All customer data is encrypted in transit using TLS 1.3 and at rest using AES-256 encryption. We also maintain SOC 2 Type II compliance."
    },
    {
        "question": "Where are your servers located?",
        "answer": "Our main server nodes are hosted on AWS in the US East (N. Virginia) region. EU customers can request data residency in the Frankfurt region."
    },
    {
        "question": "Why is the app loading so slowly today?",
        "answer": "Please check our status page at status.worksync.com for active incidents. If services are operational, try clearing browser cache and checking internet speed."
    },
    {
        "question": "How do I report a security vulnerability?",
        "answer": "Please send the details of the vulnerability to security@worksync.com. We operate a bug bounty program and request responsible disclosure."
    },
    {
        "question": "Is the app GDPR compliant?",
        "answer": "Yes, we are fully GDPR and CCPA compliant. Users can request a Data Portability Export or ask for complete deletion under the Right to be Forgotten."
    },
    {
        "question": "Does the system support IP whitelisting?",
        "answer": "Yes, Enterprise admins can set a list of allowed IP ranges under Admin Console > Security. Users connecting outside these ranges will be blocked."
    },
    {
        "question": "How do I review security audit logs?",
        "answer": "Go to Admin Settings > Audit Logs. You can filter logs by user, action type, IP address, and date, and export the logs as a CSV file."
    },
    {
        "question": "Does the app support offline mode on desktop?",
        "answer": "Yes, our desktop app for Mac and Windows caches data locally to allow offline access. Changes are queued and synced on reconnection."
    },
    {
        "question": "How do I clear local browser storage?",
        "answer": "Press F12, go to Application > Storage, click 'Clear site data'. Alternatively, log out and log back in, which clears local storage caches."
    },
    {
        "question": "What is your uptime service level agreement (SLA)?",
        "answer": "We guarantee a 99.9% uptime SLA for Enterprise plan customers, backed by financial credits if availability drops below the threshold."
    }
]
