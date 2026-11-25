import json,os,sys,shutil,datetime
sys.path.insert(0,".")
from fastlib import *
exc="NullReferenceException: Object reference not set to an instance of an object | at UIActionButton.ClickActionButton () UIActionButton.cs:42 | at InputReader.OnInventoryActionButton () InputReader.cs:100 | сообщение Unity: NullReferenceException while executing 'performed' callbacks of 'Menus/InventoryActionButton[/Keyboard/q,/AltKeyboard/q,/AltGamepad/buttonWest]'. Полный текст со стеком: INV-10_exception_editor_log.txt"
md_row("INV-10","Не пройдено","Q в открытом инвентаре (предмет Seed, Use, количество 20; 2 раза выбран другой предмет и возврат): исключение %s. После этого игра перестала отвечать: SDK без ответа с 15:23 (CommandResponseTimeoutException, 6 запросов за 3 мин), Editor.log не растёт (0 байт за 5 с). Количество до/после Q не записано (скрипт оборвался на Q). Текст исключения совпадает с CC-81, но здесь без диалога"%exc,"INV-10_exception_editor_log.txt")
st=load_state(); st["stopped_at"]=datetime.datetime.now().isoformat(timespec="seconds"); st["stop_reason"]="INV-10: NullReferenceException UIActionButton.cs:42, игра зависла"
st["note_restore"]="autoSyncTransforms True (исходное False), runInBackground True (исходное True)"
save_state(st)
bk=st["backup_dir"]
for sub,sd in (("Unity_Technologies",SAVE_DIRS[0]),("Unity_Open_Projects",SAVE_DIRS[1])):
    for f in ("save.chop","save.chop.bak"):
        src=os.path.join(bk,sub,f)
        if os.path.exists(src): shutil.copy2(src,os.path.join(sd,f))
print("возврат копии, хеши совпали:",save_hashes()==st["saves_hash_before"])
md_note("""## Остановка прогона 2 (15:23)

**Нужна помощь владельца: игра зависла после Q в INV-10 (NullReferenceException UIActionButton.cs:42), SDK и Editor.log молчат; вероятно, Unity на паузе по ошибке — нажмите Pause в Unity и снимите паузу.**

Не выполнено из блока B: INT-03, LOC-03 с DTH-03/04 и ENM-01…03, INT-06/07, INV-13, DLG-11 (порядок плана сохранён, DLG-11 последним). Сохранения возвращены из копии `save_backup\20261122_122526`, хеши совпали с исходными. На момент остановки Physics.autoSyncTransforms = True (исходное False), Application.runInBackground = True (исходное True): autoSync вернуть после возобновления.
""")
