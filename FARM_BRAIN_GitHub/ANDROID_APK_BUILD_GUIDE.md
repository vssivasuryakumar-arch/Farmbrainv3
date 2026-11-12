# FARM BRAIN Android APK build and install guide

The Android project is a WebView client. It loads your deployed FARM BRAIN website, so the website/server must be running for the app's pages, OTP, messages and database to work.

## Before building

Open `android/app/src/main/res/values/strings.xml` and set `default_website_url` to your real deployed HTTPS Render service URL. Do not leave the older demo URL unless that is where the current application is deployed.

The WebView file picker accepts JPG/JPEG, PNG, WEBP and PDF, so members can upload farm photos or attach a PDF in private messages.

## Build with GitHub Actions

1. Push the complete repository, including the `android/` folder and `.github/workflows/build-android-apk.yml`.
2. Open GitHub → Actions → `Build FARM BRAIN Android APK`.
3. Run the workflow or let a push to `main` start it.
4. Wait for the green success status.
5. Open that workflow run, scroll to Artifacts and download `farm-brain-android-debug-apk`.
6. Extract the ZIP and install `app-debug.apk` on an Android phone. Android may ask you to allow installation from the browser/files app.

## What this APK is

- Debug APK for pilot testing; not Play Store signed.
- Uses Android WebView to show the web app.
- Supports browser back navigation, external link handling and photo/PDF file selection.
- Does not itself implement a separate offline database, background sensor collection, OTP email service or cloud storage.

For a Play Store release, configure a secure signing key in a secret manager, produce a release build, test on representative Android devices, and complete privacy/data-safety declarations.
