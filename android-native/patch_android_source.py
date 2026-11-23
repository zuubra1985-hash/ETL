from pathlib import Path
import sys

target = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/arm-etl-android/app/src/main/java/ru/surgutperevalka/armetl/MainActivity.java")
source = target.read_text(encoding="utf-8")

replacements = [
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
