from pathlib import Path
import sys

target = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/arm-etl-android/app/src/main/java/ru/surgutperevalka/armetl/MainActivity.java")
source = target.read_text(encoding="utf-8")

replacements = [
    (
        "    private void loadLocalData() {\n        baseUrl = localStore.get(\"server_url\", \"\");\n        try { accessKey = SecretStore.read(this); } catch (Exception e) { accessKey = \"\"; }\n        try {\n            String raw = localStore.get(\"state\", \"\");\n            state = raw.isEmpty() ? new JSONObject() : new JSONObject(raw);\n            if (!state.has(\"si\") || !state.has(\"siz\")) state = bootstrap().optJSONObject(\"state\");\n        } catch (Exception e) { state = bootstrap().optJSONObject(\"state\"); }\n        try { reportMeta = new JSONObject(localStore.get(\"report_meta\", \"{}\")); } catch (Exception e) { reportMeta = new JSONObject(); }\n        stateEtag = localStore.get(\"state_etag\", \"\");\n        objects = readArray(\"objects\", bootstrap().optJSONArray(\"objects\"));\n        equipment = readArray(\"equipment\", bootstrap().optJSONArray(\"equipment\"));\n        calendar = readArray(\"calendar\", bootstrap().optJSONObject(\"calendar\").optJSONArray(\"months\"));\n        personnel = readArray(\"personnel\", bootstrap().optJSONArray(\"personnel\"));\n        permits = readArray(\"permits\", bootstrap().optJSONArray(\"permits\"));\n        rostech = readArray(\"rostech\", bootstrap().optJSONArray(\"rostech\"));\n        attachments = readArray(\"attachments\", new JSONArray());\n        persistStateOnly();\n    }",
        "    private void loadLocalData() {\n        baseUrl = localStore.get(\"server_url\", \"\");\n        try { accessKey = SecretStore.read(this); } catch (Exception e) { accessKey = \"\"; }\n        JSONObject defaults = bootstrap();\n        JSONObject defaultState = defaults.optJSONObject(\"state\");\n        try {\n            String raw = localStore.get(\"state\", \"\");\n            state = raw.isEmpty() ? (defaultState == null ? new JSONObject() : defaultState) : new JSONObject(raw);\n            if (!state.has(\"si\") || !state.has(\"siz\")) state = defaultState == null ? new JSONObject() : defaultState;\n        } catch (Exception e) { state = defaultState == null ? new JSONObject() : defaultState; }\n        try { reportMeta = new JSONObject(localStore.get(\"report_meta\", \"{}\")); } catch (Exception e) { reportMeta = new JSONObject(); }\n        stateEtag = localStore.get(\"state_etag\", \"\");\n        objects = readArray(\"objects\", defaults.optJSONArray(\"objects\"));\n        equipment = readArray(\"equipment\", defaults.optJSONArray(\"equipment\"));\n        JSONObject defaultCalendar = defaults.optJSONObject(\"calendar\");\n        calendar = readArray(\"calendar\", defaultCalendar == null ? new JSONArray() : defaultCalendar.optJSONArray(\"months\"));\n        personnel = readArray(\"personnel\", defaults.optJSONArray(\"personnel\"));\n        permits = readArray(\"permits\", defaults.optJSONArray(\"permits\"));\n        rostech = readArray(\"rostech\", defaults.optJSONArray(\"rostech\"));\n        attachments = readArray(\"attachments\", new JSONArray());\n        persistStateOnly();\n    }",
        1,
    ),
    (
        "    private JSONObject bootstrap() {\n        try (InputStream raw = getAssets().open(\"bootstrap.json.gz\"); GZIPInputStream in = new GZIPInputStream(raw)) {\n            return new JSONObject(new String(readAll(in), StandardCharsets.UTF_8));\n        } catch (Exception e) { return new JSONObject(); }\n    }",
        "    private JSONObject bootstrap() {\n        try {\n            byte[] data;\n            try (InputStream input = getAssets().open(\"bootstrap.json\")) {\n                data = readAll(input);\n            } catch (Exception missingPlainAsset) {\n                try (InputStream input = getAssets().open(\"bootstrap.json.gz\")) {\n                    data = readAll(input);\n                }\n            }\n            String json = new String(data, StandardCharsets.UTF_8).trim();\n            if (!json.startsWith(\"{\")) {\n                try (GZIPInputStream input = new GZIPInputStream(new java.io.ByteArrayInputStream(data))) {\n                    json = new String(readAll(input), StandardCharsets.UTF_8);\n                }\n            }\n            return new JSONObject(json);\n        } catch (Exception e) {\n            android.util.Log.e(\"ARM_ETL\", \"Не удалось загрузить встроенную базу приложения\", e);\n            return new JSONObject();\n        }\n    }",
        1,
    ),
    (
        '            rows.put(rowIndex,updated);try{proto.put("rows",rows);list.put(protocolIndex,proto);state.put("protocols",list);}catch(Exception ignored){}saveState("Изменение измерений");renderProtocolRowsEditor(protocolIndex);',
        '            try{rows.put(rowIndex,updated);proto.put("rows",rows);list.put(protocolIndex,proto);state.put("protocols",list);}catch(Exception ignored){}saveState("Изменение измерений");renderProtocolRowsEditor(protocolIndex);',
        1,
    ),
    (
        '        runAsync(()->{\n            ApiClient.Result result=api.request("POST",path,body,null);\n            if(!result.ok())throw new Exception("Сервер вернул HTTP "+result.status+": "+result.text());\n            runOnUiThread(()->startExport(result.bytes,filename,mime));\n        },e->showToast("Ошибка генерации: "+e.getMessage()));',
        '        runAsync((Work)()->{\n            ApiClient.Result result=api.request("POST",path,body,null);\n            if(!result.ok())throw new Exception("Сервер вернул HTTP "+result.status+": "+result.text());\n            runOnUiThread(()->startExport(result.bytes,filename,mime));\n            return "";\n        },e->showToast("Ошибка генерации: "+e.getMessage()));',
        1,
    ),
    (
        '        runAsync(()->{\n            ApiClient.Result response=api.requestBytes("GET","/api/backup",null,null,null,null);\n            if(!response.ok())throw new Exception("HTTP "+response.status+": "+response.text());\n            runOnUiThread(()->startExport(response.bytes,"ARM_ETL_Backup_"+new SimpleDateFormat("yyyyMMdd_HHmm",Locale.US).format(new Date())+".zip","application/zip"));\n        },e->showToast("Не удалось скачать резервную копию: "+e.getMessage()));',
        '        runAsync((Work)()->{\n            ApiClient.Result response=api.requestBytes("GET","/api/backup",null,null,null,null);\n            if(!response.ok())throw new Exception("HTTP "+response.status+": "+response.text());\n            runOnUiThread(()->startExport(response.bytes,"ARM_ETL_Backup_"+new SimpleDateFormat("yyyyMMdd_HHmm",Locale.US).format(new Date())+".zip","application/zip"));\n            return "";\n        },e->showToast("Не удалось скачать резервную копию: "+e.getMessage()));',
        1,
    ),
    (
        '        runAsync(()->{\n            ApiClient.Result r=api.request("GET","/api/attachments?entity_id="+ApiClient.encode(entityId),null,null);',
        '        runAsync((Work)()->{\n            ApiClient.Result r=api.request("GET","/api/attachments?entity_id="+ApiClient.encode(entityId),null,null);',
        1,
    ),
    (
        '            });\n        },e->showToast("Не удалось загрузить список вложений: "+e.getMessage()));',
        '            });\n            return "";\n        },e->showToast("Не удалось загрузить список вложений: "+e.getMessage()));',
        1,
    ),
    (
        '        runAsync(()->{\n            ApiClient.Result r=api.requestBytes("GET","/api/attachments/file/"+ApiClient.encode(id),null,null,null,null);\n            if(!r.ok())throw new Exception("HTTP "+r.status);\n            String mime=str(attachment,"mimeType");if(mime.isEmpty())mime="application/octet-stream";\n            runOnUiThread(()->startExport(r.bytes,name,mime));\n        },e->showToast("Не удалось скачать вложение: "+e.getMessage()));',
        '        runAsync((Work)()->{\n            ApiClient.Result r=api.requestBytes("GET","/api/attachments/file/"+ApiClient.encode(id),null,null,null,null);\n            if(!r.ok())throw new Exception("HTTP "+r.status);\n            String mimeValue=str(attachment,"mimeType");if(mimeValue.isEmpty())mimeValue="application/octet-stream";\n            final String exportMime=mimeValue;\n            runOnUiThread(()->startExport(r.bytes,name,exportMime));\n            return "";\n        },e->showToast("Не удалось скачать вложение: "+e.getMessage()));',
        1,
    ),
    (
        '    private void processPickedFile(Uri uri,String purpose){\n        runAsync(()->{',
        '    private void processPickedFile(Uri uri,String purpose){\n        runAsync((Work)()->{',
        1,
    ),
    (
        '                if(!r.ok())throw new Exception(r.text());runOnUiThread(()->showToast("Скан прикреплён к записи."));\n            }\n        },e->showToast("Ошибка обработки файла: "+e.getMessage()));',
        '                if(!r.ok())throw new Exception(r.text());runOnUiThread(()->showToast("Скан прикреплён к записи."));\n            }\n            return "";\n        },e->showToast("Ошибка обработки файла: "+e.getMessage()));',
        1,
    ),
    (
        '        runAsync(()->{\n            try(OutputStream out=getContentResolver().openOutputStream(uri,"w")){if(out==null)throw new Exception("Не удалось открыть место сохранения");out.write(bytes);out.flush();}\n            runOnUiThread(()->showToast("Файл сохранён: "+pendingExportName));\n        },e->showToast("Ошибка сохранения файла: "+e.getMessage()));',
        '        runAsync((Work)()->{\n            try(OutputStream out=getContentResolver().openOutputStream(uri,"w")){if(out==null)throw new Exception("Не удалось открыть место сохранения");out.write(bytes);out.flush();}\n            runOnUiThread(()->showToast("Файл сохранён: "+pendingExportName));\n            return "";\n        },e->showToast("Ошибка сохранения файла: "+e.getMessage()));',
        1,
    ),
]

for old, new, expected in replacements:
    count = source.count(old)
    if count != expected:
        raise SystemExit(f"Expected {expected} occurrence(s), found {count}: {old[:100]!r}")
    source = source.replace(old, new, expected)

target.write_text(source, encoding="utf-8")
print(f"Patched {len(replacements)} Java compiler issues in {target}")
