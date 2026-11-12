FARM BRAIN — FIRST RUN / UPDATED FUNCTIONAL PILOT

LOCAL WINDOWS TEST
1. Install Python 3.12.
2. Extract the full project ZIP.
3. Double-click RUN_FARM_BRAIN.bat.
4. Wait for first-run package installation.
5. Open http://127.0.0.1:5000.
6. Register a test account. In local development with OTP_DEV_MODE=true and no SMTP, the test OTP is shown in a development-only message.

EMAIL OTP
- Real email OTP and password recovery need SMTP settings.
- For Gmail: smtp.gmail.com, port 587, TLS; use a Google App Password if required after enabling 2-Step Verification.
- Never put an App Password in GitHub or share it in chat.
- Production must use APP_ENV=production and OTP_DEV_MODE=false.

PHOTO AND ATTACHMENTS
- Public photos: community posts, profiles and marketplace listings (JPG/PNG/WEBP, max 6 MB each).
- Private inbox: PDF and image attachments (max 8 MB), viewable only by conversation participants.
- Configure Cloudinary for durable public photos. Configure Render persistent disk for private attachments.

DEPLOYMENT
1. Update the complete existing GitHub repository using GITHUB_WINDOWS_GUIDE.md.
2. Check that farm_brain/, android/, tests/, docs/ and .github/workflows/ are all present.
3. Connect Render using render.yaml and configure SMTP secrets.
4. Change the Android default_website_url to your real deployed HTTPS URL.
5. Build the APK through GitHub Actions and download farm-brain-android-debug-apk.

IMPORTANT LIMITS
- ZIP contains source code and APK build automation; it does not contain a compiled APK binary.
- Full Flask tests must run in GitHub Actions. Python syntax/template/XML/YAML static checks passed in the authoring environment, but full runtime tests could not be run because Flask packages could not be installed here.
- IoT sensors, live aquaponics telemetry, native offline app data, payment rails, SMS OTP and Play Store signing are not included in this release.
