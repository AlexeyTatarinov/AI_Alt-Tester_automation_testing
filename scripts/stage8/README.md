# stage8: статические данные уровней (collect.py)

Только чтение через AltTester Python SDK 2.4.1. Навигация только меню читов (`elib.goto`), телепорта и `set_component_property` нет.
Все команды драйвера ограничены 20 вызовами/с (патч `WebsocketConnection.send`). Реально упирается в FPS редактора (в stage7 около 6 вызовов/с).

```
cd Test_Ai\scripts\stage8
..\sdk_smoke\.venv\Scripts\python.exe collect.py --probe                # 1–3 мин, текущая сцена, без навигации -> probe.json
..\sdk_smoke\.venv\Scripts\python.exe collect.py                        # все 10 локаций, продолжает с места остановки
..\sdk_smoke\.venv\Scripts\python.exe collect.py --location Forest      # одна (или несколько через запятую)
..\sdk_smoke\.venv\Scripts\python.exe collect.py --redo --location Beach
```
Полезные флаги: `--scene-seconds N` (лимит на сцену, недочитанное продолжится), `--no-ground`, `--no-tris`, `--ray-points 300`, `--ray-seconds 300`, `--fresh` (старый файл -> `.bak_*`).

Результат: `Reports_2026-11-21\results\stage8_levels\levels.json`, сохраняется каждые ~15 с и в конце каждой фазы.
- `locations.<loc>`: переход, `viewpoint` (UnityStats drawCalls/setPassCalls/triangles/vertices/batches, медиана 3 чтений; позиции игрока и камеры; FPS; размер экрана).
- `scenes.<scene>`: одна запись на `.unity` (Mountain_Path собирается один раз, точек входа две). Фазы: состав (категории по корню иерархии через `Transform gameObject.scene.name`, запасной способ — имена из PersistentManagers/Gameplay.unity), счёт компонентов, рендеры (bounds, меш, вершины, материалы, тени, static batch, enabled), MeshCollider, свет/частицы/аниматоры/LODGroup, сетка Physics.Raycast, `summary`.
- Категории: `location`, `location_clone` (корень `(Clone)` в сцене локации), `player` (PigChef), `global` (PersistentManagers/Gameplay/DontDestroyOnLoad), `tool`. Подробности читаются только для объектов локации; остальные только считаются.

Static batching: `sharedMesh` у таких объектов — общий `Combined Mesh`. В `summary.vertices` бери `dedup_sum` (не-batched по объектам + каждый Combined Mesh один раз), не `naive_sum_DO_NOT_USE`. Вершины отдельного объекта внутри Combined Mesh через SDK не получить (нужен метод меша `GetSubMesh`); пишутся `staticBatchIndex`/`subMeshStartIndex`, если probe покажет, что они читаются, и исходный меш через MeshCollider того же объекта, если он есть.

Сетка земли: три луча вниз на точку (solid = все слои, кроме Ignore Raycast/Water/UI/Characters; слой Ground; слой Water), триггеры игнорируются; высоты двоичным поиском (0,5 м) для ~40 точек. Шаг подбирается под ~300 точек и пишется в `ground.params.step`. Площадь: число попаданий × шаг².

Ограничения: UnityStats показывает последний отрисованный кадр (если открыт Scene view, числа могут быть его). Ключ строки — имя+позиция; движущиеся объекты при продолжении после перезагрузки могут попасть дважды.
