# Сборка Windows-бинарника через QEMU

Windows-версия собирается в виртуалке, запущенной в VM под QEMU/KVM. Обвязка на хосте
автоматически: запускает VM, синхронизирует исходники, запускает сборку
внутри гостя и забирает готовый `.exe`.

Сам Windows-скрипт `scripts/build-windows.cmd` полностью автономен и работает
на любой настоящей Windows-машине без QEMU.

## Что нужно установить

### На хосте (Linux) — пакеты

```bash
sudo apt install qemu-system-x86 qemu-utils ovmf swtpm swtpm-tools genisoimage socat just
# если just нет в apt (старые Ubuntu): cargo install just,
# snap install just или бинарник с github.com/casey/just/releases
# опционально, для GUI-окна VM вместо VNC:
sudo apt install qemu-system-gui
```

### Необходимые файла

| Файл | Откуда | Примечание |
|---|---|---|
| `windows.iso` | microsoft.com/software-download/windows11 (или windows10) | скачать вручную, положить в `.vm/windows-builder/` (или задать `AGIO_WIN_ISO=...`) |
| `virtio-win.iso` | fedorapeople (ссылка в `common.sh`) | скачивается автоматически при `create-vm.sh` |

### В гостевой системе Windows (ставится один раз)

- Windows 10/11 x64 (активация для сборки не нужна)
- пользователь `Admin` (SSH-обвязка использует именно его)
- OpenSSH Server (включает `guest-setup.ps1`)
- Git (`winget install Git.Git`) — нужен для зависимости `agio-core` из git
- uv (`winget install astral-sh.uv`) — python 3.11 и все зависимости
- C-компилятор: НЕ обязателен — Nuitka с `--assume-yes-for-downloads` сам
  скачивает gcc (winlibs) при первой сборке. Для MSVC поставьте
  Visual Studio 2022 Build Tools (C++ workload) — Nuitka предпочтёт его.
- virtio-драйверы: `virtio-win-guest-tools.exe` с второго CD после установки Windows

## One-time подготовка

**Автоматическая подготовка**

```bash
# 0. скачать Windows ISO и положить в .vm/windows-builder/windows.iso
# 1. установить и настроить Windows одной командой
just setup-build     # или: bash scripts/qemu/install-windows.sh
```

Скрипт идемпотентен: если Windows уже стоит и SSH отвечает — сразу выйдёт.

Два режима, в зависимости от наличия пользовательского файла ответов
`.vm/windows-builder/autounattend.xml` (рекомендуется генератор
schneegans.de/windows/unattend-generator — он сам разворачивает образ,
ставит virtio-драйверы и подтягивает наш `$OEM$` с корня unattended-ISO):
- **файл есть**: используется как есть; создаёт пользователя `Admin`
  (SSH-обвязка использует его), настройка гостя (sshd/git/uv/ключ) — нашим
  SetupComplete; завершение определяется по появлению SSH, затем grace-пауза
  на first-logon скрипты и выключение;
- **файла нет**: встроенный шаблон autounattend (wipe диска, пользователь
  `builder`, редакция по индексу `AGIO_WIN_IMAGE_INDEX`, по умолчанию 6 = Pro
  на стандартных consumer-ISO; для однокартиночных ISO индекс автоопускается
  до 1).

Прогресс установки можно смотреть VNC-клиентом на `127.0.0.1:5902`; логи
внутри гостя: `C:\Windows\Temp\agio-setupcomplete.log`.

Если используется нестандартный ISO: задайте индекс образа `AGIO_WIN_IMAGE_INDEX=1` (1 = Home) или другое число.

**Запуск вручную, если автоустановка не пошла**

```bash
bash scripts/qemu/create-vm.sh
```

При установке Windows:

1. Список дисков пуст → «Загрузить драйвер» → выбрать CD virtio-win →
   каталог `viostor\w11\amd64` (для Win10 — `viostor\w10\amd64`).
2. Установить Windows, создать пользователя `Admin` (его использует SSH-обвязка).
   Win11 Home требует аккаунт Microsoft и интернет; проще взять Win10/Win11 Pro/LTSC
   с локальной учёткой (на экране сети: Shift+F10 → `oobe\bypassnro` → Enter,
   вернуться назад — появится «У меня нет Интернета»).
3. После установки: запустить `virtio-win-guest-tools.exe` со второго CD
   (драйверы сети и прочее).
4. Не выключая VM, скачать/скопировать `scripts/qemu/guest-setup.ps1` в гостя
   и выполнить в elevated PowerShell, передав публичный ключ хоста
   (содержимое `.vm/windows-builder/id_ed25519.pub`):

   ```powershell
   powershell -ExecutionPolicy Bypass -File guest-setup.ps1 -SshPublicKey "ssh-ed25519 AAAA... agio-win-builder"
   ```

5. Проверка с хоста: `bash scripts/qemu/build-windows-qemu.sh --shutdown`
   должен погасить VM — значит SSH работает.

## Ежедневная сборка

```bash
bash scripts/qemu/build-windows-qemu.sh              # собрать (VM поднимется сама)
bash scripts/qemu/build-windows-qemu.sh --shutdown   # собрать и погасить VM
bash scripts/qemu/build-windows-qemu.sh --boot       # VM с GUI-окном (настройка/отладка)
```

Результат: `dist/agio_desk_installer.exe`.
Первая сборка в VM долгая (Nuitka качает gcc и компилирует всё с нуля),
последующие заметно быстрее — кэши Nuitka/uv в госте сохраняются.

## Как это работает

- VM: q35, UEFI (OVMF secboot + ключи Microsoft), TPM 2.0 через swtpm,
  virtio disk/net, KVM. SSH проброшен на `127.0.0.1:2222`.
- Транспорт: исходники передаются tar'ом поверх SSH (без .git/.venv/dist),
  в госте вызывается `scripts/build-windows.cmd`, артефакт забирается scp.
- `agio-core` гостём тянется из GitHub при `uv sync` (нужен git и интернет в VM).
- Все параметры (порты, CPU/RAM, пути) переопределяются переменными окружения —
  см. начало `scripts/qemu/common.sh`.

## Пересоздание VM

```bash
bash scripts/qemu/build-windows-qemu.sh --shutdown   # если запущена
rm -rf .vm/windows-builder                            # диск, vars, ключи
bash scripts/qemu/create-vm.sh                        # начать заново
```
