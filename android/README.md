# FARM BRAIN Android client

The Android app is a WebView client for the FARM BRAIN website. Set the correct production HTTPS service address in `app/src/main/res/values/strings.xml` before building. The app also includes a settings menu to change the website address on the device.

The WebView supports JavaScript/DOM storage for the responsive website, secure HTTPS-only navigation into the configured app domain, Android back navigation, downloads via external handlers, and file selection for JPG/JPEG, PNG, WEBP and PDF attachments. Private attachment permissions and email OTP are enforced by the web backend, not the APK.

Build a debug APK using the repository GitHub Actions workflow `Build FARM BRAIN Android APK`. This is a testing APK; a Play Store release requires a private signing key stored securely and a release build.
