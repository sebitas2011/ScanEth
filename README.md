ScanEth: Mapeo de Redes Wi-Fi
ScanEth es una herramienta de mapeo de redes Wi-Fi que permite visualizar la calidad de la señal de las redes disponibles en un área determinada, utilizando un sistema basado en ESP32 para el escaneo de redes y un módulo GPS para obtener las coordenadas geográficas de cada punto. El sistema proporciona un mapa interactivo que muestra la intensidad de la señal Wi-Fi clasificada como buena, intermedia o mala.

Descripción
Este proyecto tiene como objetivo ayudar a localizar las mejores zonas para conectarse a redes Wi-Fi dentro de un campus universitario (o cualquier área similar), brindando una forma sencilla de visualizar la cobertura de señal en un mapa interactivo en tiempo real.

Funcionalidades
Escaneo de Redes Wi-Fi: El ESP32 escanea las redes Wi-Fi cercanas y registra la intensidad de la señal (RSSI).

Ubicación Geográfica: Se utiliza un módulo GPS para capturar las coordenadas de cada punto de escaneo.

Mapa Interactivo: Los datos se visualizan en un mapa interactivo usando Folium, con diferentes colores que representan la calidad de la señal de las redes.

Frontend Web: Una interfaz web dinámica que permite a los usuarios interactuar con el mapa y consultar las redes disponibles por calidad de señal.

Backend en Flask: Servidor que permite la recopilación de datos en tiempo real y la visualización actualizada en la web.
