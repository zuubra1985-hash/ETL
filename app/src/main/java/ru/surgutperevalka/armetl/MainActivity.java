package ru.surgutperevalka.armetl;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.text.InputType;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS = "arm_etl_prefs";
    private static final String KEY_URL = "server_url";

    private WebView webView;
    private TextView tvServerUrl;
    private ValueCallback<Uri[]> filePathCallback;
    private Uri serverUri;

    private final ActivityResultLauncher<Intent> fileChooserLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
                if (filePathCallback == null) return;
                Uri[] uris = null;
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    Uri dataUri = result.getData().getData();
                    if (dataUri != null) uris = new Uri[]{dataUri};
                }
                filePathCallback.onReceiveValue(uris);
                filePathCallback = null;
            });

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        tvServerUrl = findViewById(R.id.tvServerUrl);
        Button btnReload = findViewById(R.id.btnReload);
        Button btnSettings = findViewById(R.id.btnSettings);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        // Uploads use Android's content picker. Local file URLs are not needed.
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setDatabaseEnabled(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportMultipleWindows(false);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (isSameServerOrigin(request.getUrl())) return false;
                Toast.makeText(MainActivity.this, "Переход на другой сайт заблокирован", Toast.LENGTH_SHORT).show();
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    Toast.makeText(MainActivity.this,
                            "Нет связи с ноутбуком. Проверьте start.bat и Tailscale/Wi-Fi.",
                            Toast.LENGTH_LONG).show();
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                filePathCallback = callback;
                try {
                    fileChooserLauncher.launch(params.createIntent());
                } catch (Exception e) {
                    filePathCallback = null;
                    Toast.makeText(MainActivity.this, "Не удалось открыть выбор файла", Toast.LENGTH_SHORT).show();
                    return false;
                }
                return true;
            }
        });

        webView.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
            try {
                Uri downloadUri = Uri.parse(url);
                if (!isSameServerOrigin(downloadUri)) {
                    Toast.makeText(this, "Загрузка с другого сайта заблокирована", Toast.LENGTH_SHORT).show();
                    return;
                }
                DownloadManager.Request request = new DownloadManager.Request(downloadUri);
                String fileName = URLUtil.guessFileName(url, contentDisposition, mimetype);
                request.setMimeType(mimetype);
                request.addRequestHeader("User-Agent", userAgent);
                // DownloadManager does not share WebView's session automatically.
                String cookie = CookieManager.getInstance().getCookie(url);
                if (cookie != null && !cookie.isEmpty()) request.addRequestHeader("Cookie", cookie);
                request.setTitle(fileName);
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
                DownloadManager manager = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
                if (manager != null) manager.enqueue(request);
                Toast.makeText(this, "Загрузка файла: " + fileName, Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                Toast.makeText(this, "Ошибка загрузки файла", Toast.LENGTH_SHORT).show();
            }
        });

        btnReload.setOnClickListener(v -> webView.reload());
        btnSettings.setOnClickListener(v -> showUrlDialog());

        String savedUrl = getSavedUrl();
        if (savedUrl.isEmpty()) showUrlDialog();
        else loadServer(savedUrl);
    }

    private boolean isSameServerOrigin(Uri candidate) {
        if (serverUri == null || candidate == null || candidate.getHost() == null) return false;
        String scheme = candidate.getScheme();
        if (!"http".equalsIgnoreCase(scheme) && !"https".equalsIgnoreCase(scheme)) return false;
        int candidatePort = candidate.getPort() == -1 ? ("https".equalsIgnoreCase(scheme) ? 443 : 80) : candidate.getPort();
        int serverPort = serverUri.getPort() == -1 ? ("https".equalsIgnoreCase(serverUri.getScheme()) ? 443 : 80) : serverUri.getPort();
        return scheme.equalsIgnoreCase(serverUri.getScheme())
                && candidate.getHost().equalsIgnoreCase(serverUri.getHost())
                && candidatePort == serverPort
                && candidate.getUserInfo() == null;
    }

    private String getSavedUrl() {
        return getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_URL, "");
    }

    private String normalizeServerUrl(String raw) {
        String clean = raw == null ? "" : raw.trim();
        if (clean.isEmpty()) throw new IllegalArgumentException("Введите адрес компьютера");
        if (!clean.startsWith("http://") && !clean.startsWith("https://")) clean = "http://" + clean;
        Uri parsed = Uri.parse(clean);
        String scheme = parsed.getScheme();
        if ((!"http".equalsIgnoreCase(scheme) && !"https".equalsIgnoreCase(scheme))
                || parsed.getHost() == null
                || parsed.getUserInfo() != null
                || parsed.getPort() == 0
                || parsed.getPort() > 65535
                || (parsed.getPath() != null && !parsed.getPath().isEmpty() && !"/".equals(parsed.getPath()))
                || parsed.getQuery() != null
                || parsed.getFragment() != null) {
            throw new IllegalArgumentException("Укажите адрес сервера и порт, например http://192.168.1.50:8080");
        }
        return clean.replaceAll("/+$", "");
    }

    private void saveUrl(String url) {
        final String clean;
        try {
            clean = normalizeServerUrl(url);
        } catch (IllegalArgumentException ex) {
            Toast.makeText(this, ex.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, clean).apply();
        loadServer(clean);
    }

    private void loadServer(String url) {
        serverUri = Uri.parse(url);
        tvServerUrl.setText("АРМ ЭТЛ · " + url.replace("http://", "").replace("https://", ""));
        webView.loadUrl(url);
    }

    private void showUrlDialog() {
        EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("http://100.x.x.x:8080 или http://192.168.1.50:8080");
        input.setText(getSavedUrl());

        new AlertDialog.Builder(this)
                .setTitle("Адрес ноутбука с АРМ ЭТЛ")
                .setMessage("Введите IP-адрес ноутбука из окна «Телефон / Синхр.» (Tailscale или Wi-Fi):")
                .setView(input)
                .setPositiveButton("Подключить", (dialog, which) -> {
                    String value = input.getText().toString().trim();
                    if (!value.isEmpty()) saveUrl(value);
                })
                .setNegativeButton("Отмена", null)
                .show();
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
