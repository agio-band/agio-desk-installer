@ECHO OFF
SETLOCAL

CHCP 65001 > NUL 2>&1
CALL %~dp0agio-setup.cmd

%AGIO_CLI% desk
