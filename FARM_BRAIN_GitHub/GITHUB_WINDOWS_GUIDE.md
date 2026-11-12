# Update the existing FARM BRAIN GitHub repository

This package is an updated source release. It has **not** been pushed into GitHub by this session. Your existing repository is `https://github.com/vssivasuryakumar-arch/FARMBRAIN`.

## Important: upload the complete folder tree

The earlier APK workflow failed because files in the `android/` folder were missing from the GitHub repository. For this updated release, upload the complete extracted project, including all nested folders:

- `farm_brain/` (Python modules, templates, CSS, JavaScript and PWA assets)
- `android/` (Android app source)
- `tests/`
- `docs/`
- `.github/workflows/` (backend tests and Android APK builder)
- root files such as `requirements.txt`, `render.yaml`, `Procfile`, `.env.example`, `README.md`

Do **not** upload `.env`, passwords, Gmail App Passwords, Cloudinary secrets, signing keys or real farm/customer documents.

## Recommended upload method

The most reliable method is GitHub Desktop on a Windows computer:

1. Download and extract the `FARM_BRAIN_Full_Prototype_v3.zip` package.
2. Clone `https://github.com/vssivasuryakumar-arch/FARMBRAIN` using GitHub Desktop.
3. Back up the existing clone if you need to preserve the original demo.
4. Copy the complete extracted package contents into the cloned `FARMBRAIN` folder and allow replacement of the old prototype files.
5. Confirm the `farm_brain`, `android`, `tests`, `docs` and `.github` folders exist at the repository root.
6. Commit with message `Upgrade FARM BRAIN functional pilot prototype` and push to `main`.

If using the GitHub website, choose **Add file → Upload files** and upload the contents of the extracted folder recursively. Mobile browsers can make folder uploads difficult; check that nested files are present before committing. Do not upload only the root-level files.

## Deploy the website on Render

1. Open <https://dashboard.render.com/> and connect the `FARMBRAIN` repository.
2. Create or update the Blueprint using the root `render.yaml`.
3. Review the Singapore web service, PostgreSQL database and persistent disk resources and their current prices before applying.
4. Set `ADMIN_EMAIL` to the email address that should own moderation. Register that account after deployment.
5. Configure the SMTP values for real email OTP and password recovery. Use Render Environment secrets; never commit credentials.
6. Optionally configure Cloudinary secrets for public community/profile/listing images.
7. Deploy and check `/healthz` returns `{"status":"ok","service":"farm-brain"}`.

The current Blueprint uses a paid Render Starter web service and a persistent disk because private message attachments need persistent storage. The included managed PostgreSQL database is also not a free expiring database. Review prices and backup requirements in Render before applying.

## Configure Gmail OTP

Typical Gmail SMTP values:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sending-address@gmail.com
SMTP_PASSWORD=Google App Password (secret)
MAIL_FROM=your-sending-address@gmail.com
SMTP_USE_TLS=true
APP_ENV=production
OTP_DEV_MODE=false
```

Enable 2-Step Verification and generate a Google App Password if required by the account. Store it only as a Render secret. Do not send the secret to anyone or add it to GitHub. See `docs/EMAIL_AND_MEDIA_SETUP.md`.

## Build the Android APK

1. Set the actual deployed Render HTTPS URL in `android/app/src/main/res/values/strings.xml` (`default_website_url`).
2. Push the updated project to `main`.
3. Open GitHub → Actions → `Build FARM BRAIN Android APK`.
4. Wait for a green workflow result.
5. Download `farm-brain-android-debug-apk` from the workflow's Artifacts section.
6. Extract the ZIP and install `app-debug.apk` on your Android phone.

The Android app is a WebView client. It loads the deployed FARM BRAIN website; it does not contain its own server/database. Rebuild after changing the default website URL or Android source. The debug APK is for pilot testing, not a Play Store release.

## Preserve the original FARM BOOK materials

Keep the original FARM BOOK source files and prior `farm-brain-demo` as an archive/backup. FARM BRAIN is the current brand. Do not delete the older material until the updated deployment has been tested and backed up.
