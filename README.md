## agio.desk installer

WIP


# Custom versions

Когда открыт первый экран можно задать кастомные версии установки пакетов. Например, для тестирования.
Для этого следует вот что сделать

1. Записать в текстовом редакторе версии в таком виде:
```
agio_core:branch=dev
agio_pipe:tag=0.0.1
agio_desk:commit=d947745
```

При этом данный коммит, тег или ветка должны существовать в репозитории на github.

2. Скопировать этот текст в буфер
3. Находясь на первой странице нажать `Ctrl+v`

Если текст успешно отобразился внизу окна, то теперь во время установки будут использоваться эти версии.
Для отмены нажмите `Ctrl+R`.

Также можно указать версии в команде установки

```shell
agio-desk-setup -p agio_core:branch=dev -p agio_pipe:tag=0.0.1 -p agio_desk:commit=d947745
```

# Build

Сборка через [just](https://github.com/casey/just). Результаты кладутся в `dist/`.

## Linux

```shell
just build-linux        # или: bash scripts/build-linux.sh
```

Нужен `uv` в PATH. Скрипт сам создаёт симлинк `agio_desk_installer/assets/uv`.
Результат: `dist/agio_desk_installer`.

## Windows

Бинарник собирается в виртуальной машине QEMU/KVM с настоящей Windows
(Nuitka + PySide6 в Wine не работают). Нужен ISO Windows x64 в
`.vm/windows-builder/windows.iso` (активация не нужна; см. `.vm/windows-builder/README.txt`).

Разовая подготовка — установка и настройка Windows-VM (~20 минут, без участия человека):

```shell
just setup-build        # или: bash scripts/qemu/install-windows.sh
```

Идемпотентно: если VM уже готова, сразу выйдет. Использует пользовательский файл
ответов `.vm/windows-builder/autounattend.xml`, если он есть (см. scripts/qemu/README.md).

Ежедневная сборка (VM поднимется сама):

```shell
just build-windows      # или: bash scripts/qemu/build-windows-qemu.sh
bash scripts/qemu/build-windows-qemu.sh --shutdown   # собрать и погасить VM
```

Результат: `dist/agio_desk_installer.exe`.

## С нуля на новой машине

```shell
sudo apt install qemu-system-x86 qemu-utils ovmf swtpm swtpm-tools genisoimage socat just
# скачать ISO Windows 10/11 x64 и положить в .vm/windows-builder/windows.iso
just setup-build        # установка Windows в VM
just build-linux        # Linux-бинарник
just build-windows      # Windows-бинарник
```

Подробности, параметры VM и ручной fallback: [scripts/qemu/README.md](scripts/qemu/README.md).
