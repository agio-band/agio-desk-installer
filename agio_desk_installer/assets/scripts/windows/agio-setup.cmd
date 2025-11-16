@ECHO OFF

CHCP 65001 > NUL 2>&1
SET "CONFIG_PATH={config_dir}\custom-env.bat"
IF EXIST "%CONFIG_PATH%" (
    CALL "%CONFIG_PATH%"
)


set AGIO_CLI={agio_executable}
