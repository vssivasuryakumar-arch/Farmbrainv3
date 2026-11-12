# Email OTP, photo sharing and message attachments setup

## Email verification

The app creates a pending registration and does not create the account until a valid six-digit email OTP is submitted. Codes are hashed in the database, expire, and have a configured failed-attempt limit. Password recovery also uses an email code.

### Local development

Set:

```env
APP_ENV=development
OTP_DEV_MODE=true
```

Without SMTP credentials, the app logs a development OTP and shows it in the development-only flash message. Never deploy with this mode enabled.

### Gmail SMTP

Typical Gmail SMTP settings:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sending-address@gmail.com
SMTP_PASSWORD=YOUR_GOOGLE_APP_PASSWORD
MAIL_FROM=your-sending-address@gmail.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

Google may require 2-Step Verification and an App Password for SMTP access. The App Password is a secret, not a normal Google password. Do not paste it into ChatGPT, commit it to Git, include it in a screenshot, or save it in the Android app. Add it under Render → FARM BRAIN service → Environment.

For production:

```env
APP_ENV=production
OTP_DEV_MODE=false
COOKIE_SECURE=true
```

If SMTP is not configured in production, registration/reset email delivery fails safely. Configure SPF/DKIM/DMARC and monitor delivery/bounces before sending to large lists; Gmail consumer SMTP is a prototype option, not an ideal high-volume transactional mail service.

## Community and profile photos

Supported types: JPG/JPEG, PNG and WEBP. The server decodes the image with Pillow, limits its dimensions, re-encodes it as JPEG and uses a random generated storage name. The original upload name is only retained as metadata.

Per-image limit: 6 MB. The overall Flask request limit is 15 MB.

Optional public storage via Cloudinary:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

If Cloudinary is configured correctly, community and profile images upload to Cloudinary and return a secure URL. Without Cloudinary, they are stored under `UPLOAD_FOLDER/public/`.

## Private direct-message attachments

Supported types: PDF and JPG/JPEG/PNG/WEBP. Limit: 8 MB. The attachment route checks that the signed-in user is either the sender or recipient of the message; private files are not exposed through the public `/media/` route.

Private attachments are saved under `UPLOAD_FOLDER/private/`. On Render, the included Blueprint mounts a persistent disk at `/var/data` and sets `UPLOAD_FOLDER=/var/data/uploads`. The service must use a paid plan that supports persistent disks. If the disk is removed, message attachments are lost; include backup/retention policy before production.

## Android file picker

The WebView application accepts image and PDF MIME types so users can select crop images for community/profile forms and PDF/image files for direct messages. The APK is only a client: backend email delivery and file storage happen on the deployed FARM BRAIN website.
