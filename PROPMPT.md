
En este proyecto vamos a generar un programa en HTML con script de Python para cálculos, tablas y graficas  energéticos en combustión de un horno de biomasa  bajo las siguientes características


1.0 Rol 
Eres un ingeniero con nivel de maestría en análisis energético para la combustión de biomasa (madera, bagazo) para generar gases calientes, también eres un experto desarrollador en htlm con script de phyton para cálculos, graficas dinámicas eiteractivas

2.0 Contexto

En un horno se quema biomasa  a razón de 3000 toneladas por hora , con un poder calorífico inferior de 11367 kj/kg con una eficiencia del 90% en transferir la energía a un flujo de alimentación con un 30% de aire en exceso , el aire en exceso alimentado es a las condiciones ambientales de Bogotá Colombia

2.1.La composición en base seca del Bagazo:

Análisis elemental en base seca	
Carbono C	50,29%
Hidrogeno H2	5,82%
Oxigeno O2	42,94%
Nitrógeno N2	0,22%
Azufre  S	0,08%
Cenizas Si	0,66%
Total base seca	100,0%

La humedad total del bagazo es del : 35.090%

3.0 Instrucciones investigación y calculo

Investigar en la web las condiciones ambientales de Bogotá, para la caracterización del flujo de aire en exceso que alimenta al horno
Investigar la formulas para cálculos de humedad relativa dada la altura sobre el nivel del mar y la temperatura de bulbo seco, esto es importante para cuando cambien las condiciones
Dadas las condiciones ambientales calcular el % de humedad del aire ambiente que va a ser usado como aire en exceso
Calcular el poder calorífico superior con la composición dada de bagazo y la temperatura de llama adiabática
Calcular el poder calorífico inferior con los datos de la composición base seca y humedad del bagazo
Calcular la temperatura de gases calientes a la salida del horno considerando el poder calorífico inferior dado de 11367kj/kg de bagazo y la eficiencia del 90% en el horno
Calcular la composición de los gases de combustión  a la salida del horno
Calcular el flujo de salida de los gases de combustión en kg/h
Calcular el flujo volumétrico y la velocidad de los gases de combustión a la salida del horno , considerando que el ducto tiene un diámetro interno de 30 pulgadas.
Calcular la caída de presión de los gases de combustión en el ducto de 30 pulgadas para cada metro a la velocidad calculada en el punto 7
Calcular la perdida de temperatura por cada metro de dicto de 30" si es un ducto estándar refractario (investiga en la web)


4.0 Creación del software y documentos soporte 

4.1 Genera un documento el látex con los cálculos extremadamente en detalle explicando paso a paso, los conceptos utilizados , las ecuaciones, los datos referenciados de la web , este documento es el archivo de información para soportar el programa o software que vamos a crear en código html

4.2 Vamos a generar un software para mostrar estos cálculos todo en presentación htlm, con script de phyton para los cálculos y las graficas, todos los archivos generados van a ser cargados en un repositorio de GitHub

4.2.1 Interfaz grafica datos entrada: 

Queremos una interfaz grafica muy estética, profesional y granular con colores predominantemente verde translucido para la imagen corporativa, amarillo transparente, azul claro trasparente, rosado transparente todo según contexto de contenido , y que se pueda incluir el logo de DML ingenieros consultores, anexo la imagen en la carpeta de archivos llamada "logo.bpn"

Interfaz grafica datos de entrada, solicitar la siguiente información relevante para el análisis en esta sección el código va a pedir la siguiente información para llenar casillas de una forma muy profesional y organizada :

Datos del proyecto:

Código del proyecto
Código del documento
Dato del analista

Interfaz grafica Datos ambientales: (para la simulación con el software usaremos las condiciones de Bogotá por defecto)

Cuidad
Altura sobre el nivel del mar
Humedad relativa
Temperatura de bulbo seco



Interfaz grafica Datos para análisis: (para el análisis por defecto están los datos suministrados en la sección 1, 2 y 3)

    Describa tipo de biomasa
    Poder calorífico inferior reportado en kj/kg
    Eficiencia del horno en %
    Poder calorífico inferior Kj/kg
    Diámetro interno ducto refractario salida gases en pulgadas
    % Carbono en base seca
    %Hidrogeno molecular en base seca 
    % Oxigeno O2 en base seca
    % Nitrógeno N2 en base Seca
    % Azufre   S   en base seca
    % Cenizas inertes como Silicio en base seca
    % Porcentaje de humedad total en H2O


4.2.2 Interfaz grafica Datos de salida: 

En esta sección se deben mostrar todos los resultados de los cálculos con sus unidades

4.2.2.1 Interfaz grafica graficas y tablas generadas de salida para el Análisis de sensibilidad
El programa debe dinámicamente  ajustarse ante cualquier cambio es los datos de entrada numéricos en las graficas y tablas generados, para tal fin como análisis de sensibilidad del sistema tenemos:

Ante la variación del flujo de aire en exceso a las condiciones de los Datos dados al programa (los datos por defecto son los de la sección 1, 2 y 3) generar graficas y tablas  de temperatura, flujo y velocidad en ducto de los gases de combustión


5.0 Notas para Claude

 
Buscamos lógica , coherencia  y validación de la veracidad de los cálculos elaborados
Usa información de la web si hay alguna inconsistencia
Usa las herramientas necesarias para los cálculos , las graficas, las tablas para generar un producto al nivel de calidad de experto




 

    






