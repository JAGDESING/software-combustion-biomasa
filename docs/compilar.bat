@echo off
echo Compilando documento LaTeX...
echo.

REM Cambiar al directorio docs
cd /d "%~dp0"

REM Primer pase: generar .aux y .toc
echo Paso 1: Compilación inicial...
pdflatex -interaction=nonstopmode calculations.tex

REM Segundo pase: procesar referencias
echo.
echo Paso 2: Procesando referencias...
pdflatex -interaction=nonstopmode calculations.tex

REM Tercer paso: actualizar referencias cruzadas
echo.
echo Paso 3: Actualizando referencias...
pdflatex -interaction=nonstopmode calculations.tex

REM Verificar si se generó el PDF
if exist calculations.pdf (
    echo.
    echo ¡Compilación exitosa!
    echo PDF generado: calculations.pdf
    echo.
    pause
) else (
    echo.
    echo Error: No se pudo generar el PDF
    echo Verifique los errores en la consola
    echo.
    pause
)