# Справочник AltTester CLI

Составлено 2026-11-18 по выводу `alttester --help` и `alttester <команда> --help`. Версия CLI: 0.1.4+89289512586547a0925aa7504ef85309532c59fe.

Примеры составлены по описанию параметров из справки. Команды из примеров не выполнялись; значения (имена объектов, пути, координаты) подставьте свои.

## Общие параметры

Принимаются всеми командами (кроме отмеченных в справке отдельно):

| Параметр | Описание |
|---|---|
| `--host <host>` | AltTester host address [default: 127.0.0.1] |
| `--port <port>` | AltTester port [default: 13000] |
| `--output-mode <output-mode>` | Output mode: 'file' (snapshot to file, compact output) or 'json' (full JSON inline, legacy) [default: file] |
| `--session <session>` | Session name. Required when more than one session is live. Defaults to the only live session for routing; on `connect`, defaults to the resolved app-id when omitted. |
| `-?, -h, --help` | Show help and usage information |
| `--version` | Показать информацию о версии |

## Список команд

- [`connect`](#connect): Connect to an AltTester-instrumented game and start a persistent daemon
- [`find`](#find): Find objects in the scene
- [`click`](#click): Click on an object (desktop)
- [`tap`](#tap): Tap on an object (mobile)
- [`get-text`](#get-text): Get text from an object
- [`set-text`](#set-text): Set text on an object
- [`scene`](#scene): Get current scene or load/list scenes
- [`game-state`](#game-state): Get complete game state with object hierarchy
- [`screenshot`](#screenshot): Take a screenshot of the game
- [`press`](#press): Press a keyboard key
- [`swipe`](#swipe): Swipe between two screen coordinates
- [`scroll`](#scroll): Scroll using mouse wheel
- [`get-property`](#get-property): Get a component property value from an object
- [`set-property`](#set-property): Set a component property value on an object
- [`snapshot`](#snapshot): Capture (default) or read back a game state snapshot
- [`docs`](#docs): Access AltTester documentation
- [`install-skills`](#install-skills): Install AltTester AI Skills for Claude Code, Codex CLI, Copilot, Cursor, Goose, and other AI agents
- [`disconnect`](#disconnect): Disconnect from the persistent daemon
- [`find-at-coordinates`](#find-at-coordinates): Find object at specific screen coordinates
- [`get-all-elements`](#get-all-elements): Get all elements in the scene
- [`touch`](#touch): Manage touch gestures (begin/move/end)
- [`move-mouse`](#move-mouse): Move mouse cursor to screen coordinates
- [`reset-input`](#reset-input): Reset all input operations to neutral state
- [`wait-for-property`](#wait-for-property): Wait for a component property to reach an expected value
- [`screen-size`](#screen-size): Get the application screen size
- [`get-time-scale`](#get-time-scale): Get the current game time scale
- [`set-time-scale`](#set-time-scale): Set the game time scale (0=paused, 1=normal, <1=slow, >1=fast)
- [`key-down`](#key-down): Press and hold a keyboard key
- [`key-up`](#key-up): Release a keyboard key
- [`run-keyword`](#run-keyword): Execute a Robot Framework keyword from the project's test library
- [`run-tests`](#run-tests): Run Robot Framework tests with timestamped output and dashboard generation
- [`mcp`](#mcp): Start the MCP (Model Context Protocol) server for IDE integration
- [`start-desktop`](#start-desktop): Start the AltTester Desktop application
- [`start-game`](#start-game): Launch a game executable for testing
- [`status`](#status): Check AltTester daemon connection status
- [`apps`](#apps): List games registered on the AltTester server
- [`setup-project`](#setup-project): Download and set up an AltTester starter project for Python or .NET
- [`ios`](#ios): iOS device management commands
- [`android`](#android): Android device management commands
- [`uninstall`](#uninstall): Remove the AltTester CLI binary
- [`update`](#update): Update alttester to the latest version
- [`logs`](#logs): Show or bundle AltTester MCP diagnostics logs for support

## connect

**Описание.** Connect to an AltTester-instrumented game and start a persistent daemon

**Использование.** `alttester connect [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--app-name <app-name>` | Application name [default: unknown] |
| `--platform <platform>` | Platform (e.g. Android, iOS, Desktop) [default: unknown] |
| `--platform-version <platform-version>` | Platform version [default: unknown] |
| `--app-id <app-id>` | Application ID [default: unknown] |
| `--device-instance-id <device-instance-id>` | Device instance ID [default: unknown] |
| `--use-secure` | Use secure WebSocket (wss://) |
| `--timeout <timeout>` | Connection timeout in seconds [default: 5] |
| `--idle-timeout <idle-timeout>` | Daemon idle timeout in seconds before it exits when nothing is talking to it [default: 300] |

**Пример:**

```bash
alttester connect --host 127.0.0.1 --port 13000
```

## find

**Описание.** Find objects in the scene

**Использование.** `alttester find [<value>] [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Exact value to search for |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy (NAME, PATH, ID, TAG, LAYER, TEXT, COMPONENT) [default: NAME] |
| `--contains <contains>` | Partial text to match |
| `--all` | Return all matching objects |
| `--wait` | Wait for object to appear |
| `--timeout <timeout>` | Timeout in seconds (with --wait) [default: 20] |
| `--camera-by <camera-by>` | Camera locator strategy [default: NAME] |
| `--camera-value <camera-value>` | Camera locator value |

**Пример:**

```bash
alttester find "PigChef(Clone)"
alttester find --by TAG Player --all
alttester find --contains Button --all
```

## click

**Описание.** Click on an object (desktop)

**Использование.** `alttester click <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--camera-by <camera-by>` | Camera locator strategy [default: NAME] |
| `--camera-value <camera-value>` | Camera locator value |

**Пример:**

```bash
alttester click "Button New Game"
```

## tap

**Описание.** Tap on an object (mobile)

**Использование.** `alttester tap <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--count <count>` | Number of taps [default: 1] |
| `--camera-by <camera-by>` | Camera locator strategy [default: NAME] |
| `--camera-value <camera-value>` | Camera locator value |

**Пример:**

```bash
alttester tap "Button Play" --count 2
```

## get-text

**Описание.** Get text from an object

**Использование.** `alttester get-text <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--camera-by <camera-by>` | Camera locator strategy [default: NAME] |
| `--camera-value <camera-value>` | Camera locator value |

**Пример:**

```bash
alttester get-text "Title"
```

## set-text

**Описание.** Set text on an object

**Использование.** `alttester set-text <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--text <text> (REQUIRED)` | Text to set |
| `--camera-by <camera-by>` | Camera locator strategy [default: NAME] |
| `--camera-value <camera-value>` | Camera locator value |

**Пример:**

```bash
alttester set-text "NameInput" --text "Player1"
```

## scene

**Описание.** Get current scene or load/list scenes

**Использование.** `alttester scene [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--load <load>` | Scene name to load |
| `--list` | List all loaded scenes |

**Пример:**

```bash
alttester scene
alttester scene --list
alttester scene --load MainMenu
```

## game-state

**Описание.** Get complete game state with object hierarchy

**Использование.** `alttester game-state [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--output <output>` | Save game state to a custom file path |
| `--root <root>` | Root object name or path to filter hierarchy to a subtree |

**Пример:**

```bash
alttester game-state --root Canvas --output game-state.json
```

## screenshot

**Описание.** Take a screenshot of the game

**Использование.** `alttester screenshot [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--path <path>` | Path to save the screenshot [default: screenshot.png] |

**Пример:**

```bash
alttester screenshot --path shots/menu.png
```

## press

**Описание.** Press a keyboard key

**Использование.** `alttester press <key> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<key>` | Key code (A-Z, 0-9, Space, Return, Escape, etc.) |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--duration <duration>` | Duration in seconds [default: 0.1] |
| `--power <power>` | Press power 0.0-1.0 [default: 1] |

**Пример:**

```bash
alttester press W --duration 0.6
```

## swipe

**Описание.** Swipe between two screen coordinates

**Использование.** `alttester swipe [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--start-x <start-x> (REQUIRED)` | Start X coordinate |
| `--start-y <start-y> (REQUIRED)` | Start Y coordinate |
| `--end-x <end-x> (REQUIRED)` | End X coordinate |
| `--end-y <end-y> (REQUIRED)` | End Y coordinate |
| `--duration <duration>` | Duration in seconds [default: 0.5] |

**Пример:**

```bash
alttester swipe --start-x 200 --start-y 300 --end-x 600 --end-y 300 --duration 0.5
```

## scroll

**Описание.** Scroll using mouse wheel

**Использование.** `alttester scroll [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--vertical <vertical>` | Vertical scroll speed (positive=up) [default: -1] |
| `--duration <duration>` | Duration in seconds [default: 0.1] |

**Пример:**

```bash
alttester scroll --vertical 2 --duration 0.2
```

## get-property

**Описание.** Get a component property value from an object

**Использование.** `alttester get-property <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--component <component> (REQUIRED)` | Component name |
| `--property <property> (REQUIRED)` | Property name |
| `--assembly <assembly> (REQUIRED)` | Assembly name |
| `--max-depth <max-depth>` | Maximum depth for property traversal [default: 2] |

**Пример:**

```bash
alttester get-property "PigChef(Clone)" --component Protagonist --assembly Assembly-CSharp --property attackInput
```

## set-property

**Описание.** Set a component property value on an object

**Использование.** `alttester set-property <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--component <component> (REQUIRED)` | Component name |
| `--property <property> (REQUIRED)` | Property name |
| `--assembly <assembly> (REQUIRED)` | Assembly name |
| `--set-value <set-value> (REQUIRED)` | Value to set |

**Пример:**

```bash
alttester set-property "Door" --component DoorScript --assembly Assembly-CSharp --property isOpen --set-value true
```

## snapshot

**Описание.** Capture (default) or read back a game state snapshot

**Использование.** `alttester snapshot [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--output <output>` | Save snapshot to a custom file path (capture mode) |
| `--root <root>` | Root object name or path to filter hierarchy to a subtree (capture mode) |
| `--show` | Read and print the latest snapshot instead of capturing a new one (does not require a connected driver) |
| `--file <file>` | Path to a snapshot file to read with --show (defaults to .alttester-cli/latest) |
| `--json` | With --show, print the raw snapshot JSON instead of the rendered hierarchy |

**Пример:**

```bash
alttester snapshot --root Canvas
alttester snapshot --show
```

## docs

**Описание.** Access AltTester documentation

**Использование.** `alttester docs [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--list` | List all documentation files |
| `--read <read>` | Read a documentation file by name |
| `--search <search>` | Search documentation for a term |

**Пример:**

```bash
alttester docs --list
alttester docs --search "find objects"
```

## install-skills

**Описание.** Install AltTester AI Skills for Claude Code, Codex CLI, Copilot, Cursor, Goose, and other AI agents

**Использование.** `alttester install-skills [<skill>] [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<skill>` | Which skill to install: 'robot' (Robot Framework guided path) or 'helper' (AI helper for existing projects) |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--zip` | Export skill as a zip file for uploading to claude.ai |

**Пример:**

```bash
alttester install-skills robot
alttester install-skills helper --zip
```

## disconnect

**Описание.** Disconnect from the persistent daemon

**Использование.** `alttester disconnect [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--all` | Disconnect every live session and remove every session file. |

**Пример:**

```bash
alttester disconnect
alttester disconnect --all
```

## find-at-coordinates

**Описание.** Find object at specific screen coordinates

**Использование.** `alttester find-at-coordinates [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--x <x> (REQUIRED)` | X coordinate |
| `--y <y> (REQUIRED)` | Y coordinate |

**Пример:**

```bash
alttester find-at-coordinates --x 553 --y 189
```

## get-all-elements

**Описание.** Get all elements in the scene

**Использование.** `alttester get-all-elements [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--enabled-only` | Only return enabled objects |

**Пример:**

```bash
alttester get-all-elements
```

## touch

**Описание.** Manage touch gestures (begin/move/end)

**Использование.** `alttester touch <action> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<action>` | Touch action: begin, move, or end |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--x <x>` | X coordinate (required for begin and move) |
| `--y <y>` | Y coordinate (required for begin and move) |
| `--finger-id <finger-id>` | Finger ID for the touch operation [default: 1] |

**Пример:**

```bash
alttester touch begin --x 300 --y 200
alttester touch move --x 400 --y 200
alttester touch end
```

## move-mouse

**Описание.** Move mouse cursor to screen coordinates

**Использование.** `alttester move-mouse [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--x <x> (REQUIRED)` | X coordinate |
| `--y <y> (REQUIRED)` | Y coordinate |
| `--duration <duration>` | Duration of the movement in seconds [default: 0.1] |

**Пример:**

```bash
alttester move-mouse --x 753 --y 189 --duration 0.3
```

## reset-input

**Описание.** Reset all input operations to neutral state

**Использование.** `alttester reset-input [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester reset-input
```

## wait-for-property

**Описание.** Wait for a component property to reach an expected value

**Использование.** `alttester wait-for-property <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Object locator value |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy [default: NAME] |
| `--component <component> (REQUIRED)` | Component name |
| `--property <property> (REQUIRED)` | Property name |
| `--assembly <assembly> (REQUIRED)` | Assembly name |
| `--expected <expected> (REQUIRED)` | Expected value to wait for |
| `--timeout <timeout>` | Timeout in seconds [default: 20] |
| `--interval <interval>` | Polling interval in seconds [default: 0.5] |

**Пример:**

```bash
alttester wait-for-property "PigChef(Clone)" --component Damageable --assembly Assembly-CSharp --property IsDead --expected false --timeout 10
```

## screen-size

**Описание.** Get the application screen size

**Использование.** `alttester screen-size [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester screen-size
```

## get-time-scale

**Описание.** Get the current game time scale

**Использование.** `alttester get-time-scale [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester get-time-scale
```

## set-time-scale

**Описание.** Set the game time scale (0=paused, 1=normal, <1=slow, >1=fast)

**Использование.** `alttester set-time-scale <value> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<value>` | Time scale value (0=paused, 0.01=near-frozen, 0.5=half speed, 1=normal, 2=double speed) |

**Пример:**

```bash
alttester set-time-scale 0.5
```

## key-down

**Описание.** Press and hold a keyboard key

**Использование.** `alttester key-down <key> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<key>` | Key code (A-Z, 0-9, Space, Return, Escape, etc.) |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--power <power>` | Press power 0.0-1.0 [default: 1] |

**Пример:**

```bash
alttester key-down Mouse1
```

## key-up

**Описание.** Release a keyboard key

**Использование.** `alttester key-up <key> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<key>` | Key code (A-Z, 0-9, Space, Return, Escape, etc.) |

**Пример:**

```bash
alttester key-up Mouse1
```

## run-keyword

**Описание.** Execute a Robot Framework keyword from the project's test library

**Использование.** `alttester run-keyword [<keyword>] [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<keyword>` | Keyword name (e.g. 'Start New Game Flow', 'Click Play Button') |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--args <args>` | Arguments to pass to the keyword |
| `--list` | List all available keywords from the project's test library |

**Пример:**

```bash
alttester run-keyword --list
alttester run-keyword "Click Play Button"
```

## run-tests

**Описание.** Run Robot Framework tests with timestamped output and dashboard generation

**Использование.** `alttester run-tests [<file>] [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<file>` | Test file or directory to run (default: tests/) [default: tests/] |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--test <test>` | Run specific test by name |
| `--include <include>` | Run tests with specific tag |
| `--status` | Report the state of the current or latest test run (background runs are started by the MCP tool) |

**Пример:**

```bash
alttester run-tests tests/
alttester run-tests tests/smoke.robot --include smoke
```

## mcp

**Описание.** Start the MCP (Model Context Protocol) server for IDE integration

**Использование.** `alttester mcp [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester mcp
```

## start-desktop

**Описание.** Start the AltTester Desktop application

**Использование.** `alttester start-desktop [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester start-desktop
```

## start-game

**Описание.** Launch a game executable for testing

**Использование.** `alttester start-game <path> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<path>` | Full path to the game executable |

**Пример:**

```bash
alttester start-game "C:\Builds\ChopChop\ChopChop.exe"
```

## status

**Описание.** Check AltTester daemon connection status

**Использование.** `alttester status [options]`

**Параметры.** Своих параметров нет, только общие.

**Пример:**

```bash
alttester status
```

## apps

**Описание.** List games registered on the AltTester server

**Использование.** `alttester apps [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--timeout <timeout>` | Server query timeout in seconds [default: 5] |
| `--use-secure` | Use secure WebSocket (wss://) - match the AltServer's TLS config |

**Пример:**

```bash
alttester apps
```

## setup-project

**Описание.** Download and set up an AltTester starter project for Python or .NET

**Использование.** `alttester setup-project <language> [options]`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<language>` | Programming language: 'python' or 'dotnet' |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--name <name>` | Name of the game you're testing [default: MyGame] [default: MyGame] |
| `--path <path>` | Directory where the project will be created [default: current directory] |
| `--description <description>` | Brief description of the game for project documentation |

**Пример:**

```bash
alttester setup-project python --name ChopChop --path C:\Tests\ChopChopTests
```

## ios

**Описание.** iOS device management commands

**Использование.** `alttester ios [command] [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios devices
```

**Подкоманды `ios`:**

### ios devices

**Описание.** List connected iOS devices

**Использование.** `alttester ios devices`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios devices
```

### ios install

**Описание.** Install an .ipa or .app on an iOS device

**Использование.** `alttester ios install <app-path>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<app-path>` | Path to .ipa or .app file |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios install ./MyGame.ipa
```

### ios launch

**Описание.** Launch an app on an iOS device

**Использование.** `alttester ios launch <bundle-id>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<bundle-id>` | App bundle identifier |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios launch com.company.mygame
```

### ios uninstall

**Описание.** Uninstall an app from an iOS device

**Использование.** `alttester ios uninstall <bundle-id>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<bundle-id>` | App bundle identifier |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios uninstall com.company.mygame
```

### ios wda-setup

**Описание.** Clone and build WebDriverAgent (one-time setup)

**Использование.** `alttester ios wda-setup`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--team-id <team-id> (REQUIRED)` | Apple Developer Team ID |
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-setup
```

### ios wda-start

**Описание.** Start WebDriverAgent server on device

**Использование.** `alttester ios wda-start`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--team-id <team-id>` | Apple Developer Team ID |
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-start --device <UDID>
```

### ios wda-stop

**Описание.** Stop the WebDriverAgent server

**Использование.** `alttester ios wda-stop`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-stop
```

### ios wda-status

**Описание.** Check WebDriverAgent server status

**Использование.** `alttester ios wda-status`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-status
```

### ios wda-tap

**Описание.** Tap a native UI element on the device

**Использование.** `alttester ios wda-tap <query>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<query>` | Element name, accessibility ID, or predicate |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy: name, accessibility-id, class, predicate [default: name] |
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-tap "Allow"
```

### ios wda-find

**Описание.** Find a native UI element on the device

**Использование.** `alttester ios wda-find <query>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<query>` | Element name, accessibility ID, or predicate |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy: name, accessibility-id, class, predicate [default: name] |
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-find "Allow"
```

### ios wda-source

**Описание.** Get the native UI hierarchy from the device

**Использование.** `alttester ios wda-source`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios wda-source
```

### ios run

**Описание.** Install, launch, and set up an app for testing (composite)

**Использование.** `alttester ios run <app-path>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<app-path>` | Path to .ipa or .app file |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--team-id <team-id>` | Apple Developer Team ID (enables WDA for native UI interaction) |
| `--accept-alerts` | Auto-accept permission alerts after launch |
| `--connect` | Connect AltTester driver after launch |
| `--device <device>` | Device UDID (auto-detected if only one device connected) |

**Пример:**

```bash
alttester ios run ./MyGame.ipa
```

## android

**Описание.** Android device management commands

**Использование.** `alttester android [command] [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android devices
```

**Подкоманды `android`:**

### android devices

**Описание.** List connected Android devices and emulators

**Использование.** `alttester android devices`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android devices
```

### android install

**Описание.** Install an APK on an Android device

**Использование.** `alttester android install <apk-path>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<apk-path>` | Path to .apk file |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android install ./MyGame.apk
```

### android launch

**Описание.** Launch an app on an Android device

**Использование.** `alttester android launch <package>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<package>` | App package name (e.g. com.example.game) |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android launch com.company.mygame
```

### android uninstall

**Описание.** Uninstall an app from an Android device

**Использование.** `alttester android uninstall <package>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<package>` | App package name |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android uninstall com.company.mygame
```

### android forward

**Описание.** Set up reverse port forwarding for AltTester

**Использование.** `alttester android forward`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android forward
```

### android clear-forward

**Описание.** Remove all reverse port forwarding rules

**Использование.** `alttester android clear-forward`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android clear-forward
```

### android tap

**Описание.** Tap a native UI element on the device

**Использование.** `alttester android tap <query>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<query>` | Element text, resource-id, or class name |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy: text, resource-id, class, content-desc [default: text] |
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android tap "Allow"
```

### android find

**Описание.** Find a native UI element on the device

**Использование.** `alttester android find <query>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<query>` | Element text, resource-id, or class name |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--by <by>` | Locator strategy: text, resource-id, class, content-desc [default: text] |
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android find "Allow"
```

### android source

**Описание.** Dump the native UI hierarchy from the device

**Использование.** `alttester android source`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android source
```

### android run

**Описание.** Install, launch, and set up an app for testing (composite)

**Использование.** `alttester android run <apk-path>`

**Аргументы:**

| Аргумент | Описание |
|---|---|
| `<apk-path>` | Path to .apk file |

**Параметры:**

| Параметр | Описание |
|---|---|
| `--package <package>` | App package name (auto-detected if omitted) |
| `--forward` | Set up reverse port forwarding |
| `--connect` | Connect AltTester driver after launch |
| `--device <device>` | Device serial (auto-detected if only one device connected) |

**Пример:**

```bash
alttester android run ./MyGame.apk
```

## uninstall

**Описание.** Remove the AltTester CLI binary

**Использование.** `alttester uninstall [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--purge` | Also remove session data (~/.alttester-cli/) |
| `-y, --yes` | Skip confirmation prompt (required in non-interactive terminals such as GitBash) |

**Пример:**

```bash
alttester uninstall --yes
```

## update

**Описание.** Update alttester to the latest version

**Использование.** `alttester update [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--check` | Check for a new version without downloading |
| `--auto-update <auto-update>` | Enable or disable automatic updates on startup (on\|off) |

**Пример:**

```bash
alttester update --check
```

## logs

**Описание.** Show or bundle AltTester MCP diagnostics logs for support

**Использование.** `alttester logs [options]`

**Параметры:**

| Параметр | Описание |
|---|---|
| `--bundle` | Zip recent MCP logs and AltTester Desktop logs into one file to send to support |
| `--days <days>` | With --bundle: include logs modified in the last N days [default: 3] |
| `--output <output>` | With --bundle: path of the zip to write (default: Desktop, or ~/.alttester) |
| `--desktop-logs <desktop-logs>` | AltTester Desktop log folder (default: ~/.alttester/DesktopLogs) |
| `--no-desktop` | With --bundle: leave out AltTester Desktop logs |

**Пример:**

```bash
alttester logs
alttester logs --bundle --days 3
```
