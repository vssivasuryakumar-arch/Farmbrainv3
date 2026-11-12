package com.farmbrain.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.SslErrorHandler;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import android.net.http.SslError;
import android.graphics.Typeface;
import android.widget.PopupMenu;

public class MainActivity extends Activity {
    private static final String PREFS = "farm_brain_settings";
    private static final String KEY_URL = "website_url";
    private static final int FILE_CHOOSER_REQUEST = 4107;

    private LinearLayout root;
    private WebView webView;
    private ProgressBar progressBar;
    private TextView titleView;
    private ValueCallback<Uri[]> pendingFileCallback;
    private String websiteUrl;
    private String lastPageUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(Color.rgb(20, 45, 35));
        window.setNavigationBarColor(Color.rgb(20, 45, 35));

        SharedPreferences preferences = getSharedPreferences(PREFS, MODE_PRIVATE);
        websiteUrl = preferences.getString(KEY_URL, getString(R.string.default_website_url));
        if (!isValidHttpsUrl(websiteUrl)) {
            websiteUrl = getString(R.string.default_website_url);
        }
        lastPageUrl = websiteUrl;

        buildLayout();
        createWebView();
        if (savedInstanceState != null && webView.restoreState(savedInstanceState) != null) {
            // WebView restored its previous navigation state.
        } else {
            loadWebsite();
        }
    }

    private void buildLayout() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(245, 243, 234));
        root.setFitsSystemWindows(false);
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            int left = insets.getSystemWindowInsetLeft();
            int top = insets.getSystemWindowInsetTop();
            int right = insets.getSystemWindowInsetRight();
            int bottom = insets.getSystemWindowInsetBottom();
            view.setPadding(left, top, right, bottom);
            return insets;
        });

        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setGravity(Gravity.CENTER_VERTICAL);
        toolbar.setPadding(dp(16), 0, dp(8), 0);
        toolbar.setBackgroundColor(Color.rgb(20, 45, 35));
        toolbar.setLayoutParams(new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(58)));

        LinearLayout brand = new LinearLayout(this);
        brand.setOrientation(LinearLayout.VERTICAL);
        brand.setGravity(Gravity.CENTER_VERTICAL);
        titleView = new TextView(this);
        titleView.setText("FARM BRAIN");
        titleView.setTextColor(Color.WHITE);
        titleView.setTextSize(18);
        titleView.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        TextView subtitle = new TextView(this);
        subtitle.setText("AGRICULTURE • BUSINESS • COMMUNITY");
        subtitle.setTextColor(Color.rgb(199, 217, 122));
        subtitle.setTextSize(9);
        brand.addView(titleView);
        brand.addView(subtitle);
        toolbar.addView(brand, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1));

        Button menuButton = new Button(this);
        menuButton.setText("⋮");
        menuButton.setTextSize(24);
        menuButton.setTextColor(Color.WHITE);
        menuButton.setAllCaps(false);
        menuButton.setMinWidth(dp(44));
        menuButton.setMinimumWidth(dp(44));
        menuButton.setBackgroundColor(Color.TRANSPARENT);
        menuButton.setOnClickListener(this::showMenu);
        toolbar.addView(menuButton, new LinearLayout.LayoutParams(dp(48), dp(52)));
        root.addView(toolbar);

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(100);
        progressBar.setProgressTintList(android.content.res.ColorStateList.valueOf(Color.rgb(199, 217, 122)));
        progressBar.setProgressBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(36, 82, 60)));
        root.addView(progressBar, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(3)));

        setContentView(root);
    }

    private void createWebView() {
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(245, 243, 234));
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setMediaPlaybackRequiresUserGesture(true);
        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, false);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleNavigation(request.getUrl().toString());
            }

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleNavigation(url);
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                lastPageUrl = url;
                progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                lastPageUrl = url;
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showConnectionError();
                }
            }

            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                // Never bypass certificate errors.
                handler.cancel();
                showConnectionError();
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                if (newProgress >= 100) progressBar.setVisibility(View.GONE);
                else progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> filePathCallback,
                                             FileChooserParams fileChooserParams) {
                if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
                pendingFileCallback = filePathCallback;
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                // Support both community/profile photos and Gmail-style PDF attachments.
                intent.setType("*/*");
                intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{
                        "image/jpeg", "image/png", "image/webp", "application/pdf"
                });
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,
                        fileChooserParams.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE);
                try {
                    startActivityForResult(Intent.createChooser(intent, "Choose a photo or PDF"), FILE_CHOOSER_REQUEST);
                } catch (ActivityNotFoundException ex) {
                    pendingFileCallback = null;
                    Toast.makeText(MainActivity.this, "No photo picker is available on this phone.", Toast.LENGTH_LONG).show();
                    return false;
                }
                return true;
            }
        });

        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {
            openExternal(url);
        });
        root.addView(webView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));
    }

    private boolean handleNavigation(String rawUrl) {
        Uri uri = Uri.parse(rawUrl);
        String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase();
        if ((scheme.equals("https") || scheme.equals("http")) && isAppDomain(uri)) {
            return false;
        }
        openExternal(rawUrl);
        return true;
    }

    private boolean isAppDomain(Uri uri) {
        Uri base = Uri.parse(websiteUrl);
        String host = uri.getHost();
        String baseHost = base.getHost();
        if (host == null || baseHost == null || !"https".equalsIgnoreCase(uri.getScheme())) return false;
        host = host.toLowerCase();
        baseHost = baseHost.toLowerCase();
        return host.equals(baseHost);
    }

    private void openExternal(String rawUrl) {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(rawUrl));
            startActivity(intent);
        } catch (ActivityNotFoundException | SecurityException ex) {
            Toast.makeText(this, "No app can open this link.", Toast.LENGTH_SHORT).show();
        }
    }

    private void loadWebsite() {
        if (webView != null) {
            lastPageUrl = websiteUrl;
            progressBar.setVisibility(View.VISIBLE);
            webView.loadUrl(websiteUrl);
        }
    }

    private void showConnectionError() {
        if (webView == null) return;
        progressBar.setVisibility(View.GONE);
        String html = "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<style>body{font-family:Arial,sans-serif;background:#f5f3ea;color:#17211b;padding:32px;text-align:center}"
                + ".box{max-width:420px;margin:18vh auto}h2{color:#24523c}button{background:#24523c;color:white;border:0;"
                + "padding:14px 22px;border-radius:10px;font-size:16px}</style></head><body><div class='box'>"
                + "<h2>FARM BRAIN is not reachable</h2><p>Check your internet connection or the website deployment, then try again.</p>"
                + "<button id=\"retry\">Try again</button></div><script>document.getElementById('retry').onclick=function(){location.href="
                + jsString(lastPageUrl) + ";};</script></body></html>";
        webView.loadDataWithBaseURL("https://farm-brain.local/", html, "text/html", "UTF-8", null);
    }

    private String jsString(String value) {
        String safe = value == null ? websiteUrl : value;
        return "'" + safe.replace("\\", "\\\\").replace("'", "\\'") + "'";
    }

    private void showMenu(View anchor) {
        PopupMenu popup = new PopupMenu(this, anchor);
        popup.getMenu().add("Reload website").setOnMenuItemClickListener(item -> {
            if (webView != null) webView.reload();
            return true;
        });
        popup.getMenu().add("Set website address").setOnMenuItemClickListener(item -> {
            showWebsiteSettings();
            return true;
        });
        popup.getMenu().add("Open in browser").setOnMenuItemClickListener(item -> {
            openExternal(lastPageUrl == null ? websiteUrl : lastPageUrl);
            return true;
        });
        popup.getMenu().add("About FARM BRAIN").setOnMenuItemClickListener(item -> {
            new AlertDialog.Builder(this)
                    .setTitle("FARM BRAIN")
                    .setMessage("Your agriculture, business, livestock and farm support platform.\n\nThis Android app securely opens your deployed FARM BRAIN website.")
                    .setPositiveButton("OK", null).show();
            return true;
        });
        popup.show();
    }

    private void showWebsiteSettings() {
        EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setText(websiteUrl);
        input.setSelection(input.getText().length());
        input.setHint("https://your-farm-brain-service.onrender.com");
        input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
        int pad = dp(20);
        FrameLayout holder = new FrameLayout(this);
        holder.setPadding(pad, dp(8), pad, 0);
        holder.addView(input, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        new AlertDialog.Builder(this)
                .setTitle("FARM BRAIN website")
                .setMessage("Enter the HTTPS address of your deployed FARM BRAIN website.")
                .setView(holder)
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Save and open", (dialog, which) -> {
                    String candidate = input.getText().toString().trim();
                    if (!isValidHttpsUrl(candidate)) {
                        Toast.makeText(this, "Please enter a valid HTTPS website address.", Toast.LENGTH_LONG).show();
                        return;
                    }
                    websiteUrl = ensureTrailingSlash(candidate);
                    getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, websiteUrl).apply();
                    webView.clearHistory();
                    loadWebsite();
                }).show();
    }

    private boolean isValidHttpsUrl(String value) {
        if (value == null || value.trim().isEmpty()) return false;
        Uri uri = Uri.parse(value.trim());
        return "https".equalsIgnoreCase(uri.getScheme()) && uri.getHost() != null && uri.getHost().contains(".");
    }

    private String ensureTrailingSlash(String value) {
        return value.endsWith("/") ? value : value + "/";
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && pendingFileCallback != null) {
            Uri[] results = null;
            if (resultCode == RESULT_OK && data != null) {
                if (data.getClipData() != null) {
                    int count = data.getClipData().getItemCount();
                    results = new Uri[count];
                    for (int i = 0; i < count; i++) results[i] = data.getClipData().getItemAt(i).getUri();
                } else if (data.getData() != null) {
                    results = new Uri[]{data.getData()};
                }
            }
            pendingFileCallback.onReceiveValue(results);
            pendingFileCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        if (webView != null) webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onPause() {
        if (webView != null) webView.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) webView.onResume();
    }

    @Override
    protected void onDestroy() {
        if (pendingFileCallback != null) {
            pendingFileCallback.onReceiveValue(null);
            pendingFileCallback = null;
        }
        if (webView != null) {
            webView.stopLoading();
            webView.setWebChromeClient(null);
            webView.setWebViewClient(null);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
